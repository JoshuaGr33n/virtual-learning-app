"""
ASGI config for project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import os

# Import websocket_urlpatterns from each app
from classes.routing import websocket_urlpatterns as classes_websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'full_website.settings')

# Combine websocket_urlpatterns from all apps
combined_websocket_urlpatterns = classes_websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(), 
    "websocket": AuthMiddlewareStack(
        URLRouter(
            combined_websocket_urlpatterns 
        )
    ),
})
