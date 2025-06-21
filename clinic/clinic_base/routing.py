from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # e.g. ws://<host>/ws/chat/123/
    re_path(r"^ws/chat/(?P<conversation_id>\d+)/$", consumers.ChatConsumer.as_asgi()),

     # Clients connect to ws://…/ws/webrtc/<room_name>/
    re_path(r'ws/webrtc/(?P<calls_uuid>[0-9a-f-]+)/$', consumers.SignalingConsumer.as_asgi()),

    re_path(r"^ws/waiting-room/(?P<calls_uuid>[0-9a-f-]+)/$", consumers.WaitingRoomConsumer.as_asgi()),
]