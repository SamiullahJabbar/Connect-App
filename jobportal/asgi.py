# """
# ASGI config for jobportal project.

# It exposes the ASGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
# """

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobportal.settings')

# application = get_asgi_application()


import os
import django  # <-- Add this line
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import api.routing  # Import WebSocket routes

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobportal.settings')

# Ensure Django is fully initialized before ASGI loads
django.setup()  # <-- Add this line

# Define ASGI application
application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Handles HTTP requests
    "websocket": AuthMiddlewareStack(  # Handles WebSockets
        URLRouter(api.routing.websocket_urlpatterns)
    ),
})


