# patient/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.utils import timezone
from channels.db import database_sync_to_async

from account.models import Conversation, Message, Profile

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Called when a WebSocket connection is opened.
        We expect the URL pattern to include a conversation_id.
        """
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"chat_{self.conversation_id}"


        # Verify that the user belongs to this conversation
        user = self.scope["user"]

        if not user.is_authenticated:
            print("User is not authenticated, closing connection.")
            await self.close()
            return
        
        # Load Profile instance
        try:
            profile = await database_sync_to_async(Profile.objects.get)(user=user)
            
            print(f"Profile found for {user}")
        except Profile.DoesNotExist:
            print("Profile does not exist for the user, closing connection.")
            await self.close()
            return

        try:
            conv = await database_sync_to_async(Conversation.objects.get)(id=self.conversation_id)
            print(f"Conversation found  {self.conversation_id}")


        except Conversation.DoesNotExist:
            print(f"Conversation with id {self.conversation_id} does not exist, closing connection.")
            await self.close()
            return

        # If user is not a participant, reject
        is_participant = await database_sync_to_async(
            conv.participants.filter(id=profile.id).exists
        )()
        if not is_participant:
            print(f"User {user} is not a participant in conversation {self.conversation_id}, closing connection.")
            await self.close()
            return

        # Accept connection and add to group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """
        Called when WebSocket disconnects.
        """

        print(close_code, )
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Called when a WebSocket message is received from the client.
        We expect text_data to be JSON: {"content": "..."}.
        """
        user = self.scope["user"]

        # Get the profile safely in async context
        profile = await database_sync_to_async(Profile.objects.get)(user=user)

        # Parse incoming JSON data
        data = json.loads(text_data)
        content = data.get("content", "").strip()

        print(f"Received message content: {content}")

        if not content:
            return  # Ignore empty messages

        # Save the message to the database
        message_obj = await self.create_message(profile, content)

        # Safely access related fields for the payload
        sender_full_name = await database_sync_to_async(lambda: profile.user.first_name)()
        sender_username = await database_sync_to_async(lambda: profile.user.username)()
        sender_pic = await database_sync_to_async(lambda: profile.profile_pic.url if profile.profile_pic else None)()
        message_content = await database_sync_to_async(lambda: message_obj.content)()
        message_id = await database_sync_to_async(lambda: message_obj.id)()
        message_read = await database_sync_to_async(lambda: message_obj.read)()
        message_timestamp = await database_sync_to_async(lambda: message_obj.timestamp)()
        timestamp_local = timezone.localtime(message_timestamp).strftime("%I:%M %p, %d %b %Y")

        

        # Prepare payload
        payload = {
            "conversation_id": self.conversation_id,
            "msg_by_me": True,
            "id": message_id,
            "sender": sender_full_name,
            "sender_pic" : sender_pic,
            "username": sender_username,
            "content": message_content,
            "timestamp": timestamp_local,
            "read": message_read,
        }

        # Send message to the sender only with msg_by_me=True
        await self.send(text_data=json.dumps(payload))

        # Prepare payload for others (msg_by_me=False)
        payload["msg_by_me"] = False


        # Broadcast to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": payload,
            }
        )

    async def chat_message(self, event):
        """
        Handler for messages sent to the group.
        Will be called for every consumer in the group.
        """
        message = event["message"]
        # Determine if it was sent by this connection’s user
        # (We’ll rely on the payload’s "msg_by_me" to guide the front‐end.)
        await self.send(text_data=json.dumps(message))

    @database_sync_to_async
    def create_message(self, sender_profile, content):
        """
        Create and return a Message instance in the DB.
        """
        conv = Conversation.objects.get(id=self.conversation_id)
        # By default, read=False for the newly created message
        msg = Message.objects.create(
            conversation=conv,
            sender=sender_profile,
            content=content,
            read=False
        )
        return msg
