from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ChatMessage
from .serializers import ChatMessageSerializer

class ChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, receiver_username):
        messages = ChatMessage.objects.filter(
            sender=request.user, receiver__username=receiver_username
        ) | ChatMessage.objects.filter(
            sender__username=receiver_username, receiver=request.user
        ).order_by("timestamp")

        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data, status=200)
