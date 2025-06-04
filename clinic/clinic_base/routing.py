from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # e.g. ws://<host>/ws/chat/123/
    re_path(r"^ws/chat/(?P<conversation_id>\d+)/$", consumers.ChatConsumer.as_asgi()),
]