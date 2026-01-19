"""
WebSocket routing for real-time sign detection
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/detection/$', consumers.SignDetectionConsumer.as_asgi()),
    re_path(r'ws/session/(?P<session_id>\w+)/$', consumers.SessionConsumer.as_asgi()),
]
