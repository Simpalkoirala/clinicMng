# patient/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.utils import timezone
from channels.db import database_sync_to_async

from account.models import Conversation, Message, Profile, Calls

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
        except Profile.DoesNotExist:
            print("Profile does not exist for the user, closing connection.")
            await self.close()
            return

        try:
            conv = await database_sync_to_async(Conversation.objects.get)(id=self.conversation_id)
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

        print(message_read, "message_read")

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

        # if conv status is requested, then change to 'active'
        if conv.status == 'requested':
            conv.status = 'active'
            conv.save() 

        # By default, read=False for the newly created message
        msg = Message.objects.create(
            conversation=conv,
            sender=sender_profile,
            content=content,
            read=False
        )
        return msg


class SignalingConsumer(AsyncWebsocketConsumer):
    all_connected_users = {}

    async def connect(self):
        self.calls_uuid = self.scope['url_route']['kwargs']['calls_uuid']
        self.room_group_name = f'webrtc_{self.calls_uuid}'
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        username = self.user.username
        room_users = SignalingConsumer.all_connected_users.setdefault(self.room_group_name, [])
        if username not in room_users:
            room_users.append(username)
        self.connected_users = room_users

        await self.accept()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'signal_message',
                'sender_channel': self.channel_name,
                'sendToSender': True,
                'message': {
                    'request_type': 'user_joined',
                    'connected_users': self.connected_users,
                    'new_user': username,
                }
            }
        )

    async def disconnect(self, close_code):
        username = self.user.username
        room_users = SignalingConsumer.all_connected_users.get(self.room_group_name, [])
        if username in room_users:
            room_users.remove(username)
        if not room_users:
            SignalingConsumer.all_connected_users.pop(self.room_group_name, None)

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'signal_message',
                'sender_channel': self.channel_name,
                'message': {
                    'request_type': 'user_left',
                    'connected_users': room_users,
                    'left_user': username,
                }
            }
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        # Forward SDP and ICE messages to everyone else
        if message_type in ['offer', 'answer', 'ice-candidate']:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'signal_message',
                    'sender_channel': self.channel_name,
                    'message': data
                }
            )
        elif message_type == 'call-ended':
            call_uuid = data.get('roomName')

            # Update the call status to 'ended' in the database
            call_obj = await database_sync_to_async(Calls.objects.get)(uuid=call_uuid)
            call_obj.status = 'completed'
            await database_sync_to_async(lambda: call_obj.save())()
            


            # Handle call ended message
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'signal_message',
                    'sender_channel': self.channel_name,
                    'message': {
                        'request_type': 'call-ended',
                        'message': f'{data.get('username')} has ended the call.'
                    }
                }
            )

    async def signal_message(self, event):
        sendToSender = event.get('sendToSender', False)
        if not sendToSender:
            # Don't send to the sender
            if event['sender_channel'] != self.channel_name:
                await self.send(text_data=json.dumps(event['message']))
        else:
            # Send to the sender
            await self.send(text_data=json.dumps(event['message']))

class WaitingRoomConsumer(AsyncWebsocketConsumer):
    # Shared user storage for all rooms
    all_connected_users = {}

    async def connect(self):
        self.calls_uuid = self.scope['url_route']['kwargs']['calls_uuid']
        self.room_group_name = f'waiting_room_{self.calls_uuid}'
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Track this user
        username = self.user.username
        room_users = WaitingRoomConsumer.all_connected_users.setdefault(self.room_group_name, [])

        if username not in room_users:
            room_users.append(username)

        self.connected_users = room_users

        print(f"User {username} connected to waiting room {self.room_group_name}. Connected users: {self.connected_users}")

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'waiting_room_message',
                'message': {
                    'request_type': 'user_joined',
                    'connected_users': self.connected_users,
                    'new_user': username,
                }
            }
        )
        await self.accept()


    async def disconnect(self, close_code):
        username = self.user.username
        room_users = WaitingRoomConsumer.all_connected_users.get(self.room_group_name, [])

        if username in room_users:
            room_users.remove(username)

        if not room_users:
            WaitingRoomConsumer.all_connected_users.pop(self.room_group_name, None)

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'waiting_room_message',
                'message': {
                    'request_type': 'user_left',
                    'disconnected_user': username,
                    'connected_users': room_users,
                }
            }
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        request_type = data.get('request_type')
        if request_type == 'request_to_active':
            call_uuid = data.get('call_uuid')
            call_obj = await database_sync_to_async(Calls.objects.get)(uuid=call_uuid)
            call_obj.status = 'active'
            await database_sync_to_async(lambda: call_obj.save())()

        elif request_type == 'request_to_join':
            call_uuid = data.get('call_uuid')
            call_obj = await database_sync_to_async(Calls.objects.get)(uuid=call_uuid)
            call_obj.last_req = timezone.now()
            await database_sync_to_async(lambda: call_obj.save())()
            # Send notification to doctor
            # await self.channel_layer.group_send(
            #     f'notification_{call_obj.doctor.id}',
            #     {
            #         'type': 'send_notification',
            #         'notification': {
            #             'type': 'join_request',
            #             'message': f'{self.user.username} wants to join the call',
            #             'call_uuid': str(call_uuid)
            #         }
            #     }
            # )



    async def waiting_room_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))



class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        self.room_group_name = f'notification_{self.user.id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        # This consumer is for receiving notifications, so we don't expect to receive messages
        pass

    async def send_notification(self, event):
        notification = event['notification']
        await self.send(text_data=json.dumps(notification))