import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from .models import ChatMessage

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handles WebSocket connection"""
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        # Authenticate user properly
        self.user = await self.get_user_instance(self.scope["user"])

        if not self.user:
            await self.close()  # Close connection if user is not authenticated
            return

        # Join chat room
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Handles WebSocket disconnection"""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Handles messages received from WebSocket"""
        data = json.loads(text_data)
        receiver_username = data.get("receiver")
        message = data.get("message")

        if not receiver_username or not message:
            return

        try:
            receiver = await database_sync_to_async(User.objects.get)(username=receiver_username)
        except User.DoesNotExist:
            return

        # Save message in database
        await database_sync_to_async(ChatMessage.objects.create)(
            sender=self.user, receiver=receiver, message=message
        )

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": self.user.username,
            }
        )

    async def chat_message(self, event):
        """Handles messages sent to WebSocket"""
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"]
        }))

    @database_sync_to_async
    def get_user_instance(self, user):
        """Fix UserLazyObject issue by converting it to User instance"""
        if user.is_authenticated:
            return User.objects.get(id=user.id)
        return None
