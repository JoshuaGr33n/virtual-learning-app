from django.urls import path
from channels.routing import URLRouter
from . import consumers

websocket_urlpatterns = [
    path(r'ws/class/<uuid:class_id>/', consumers.Consumer.as_asgi()),
]
