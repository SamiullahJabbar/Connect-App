from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .serializers import RegisterSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserDetailSerializer,ChatMessageSerializer,CustomTokenObtainPairSerializer,FCMDeviceSerializer
from .models import UserProfile,ChatMessage,FCMDevice
from django.db import models
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
from rest_framework.viewsets import ModelViewSet


User = get_user_model()
User.add_to_class('user_type', models.CharField(max_length=10, choices=[('buyer', 'Buyer'), ('seller', 'Seller')], null=True, blank=True, default='buyer'))

# Initialize Firebase Admin SDK
cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred)

class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['POST'])
def change_the_user_status(request):
    status = request.data.get('status')
    user = request.user
    user.user_type = status
    user.save()
    return Response({"message": "User type changed to " + status}, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the refresh token
            return Response({"message": "Successfully logged out"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

from .serializers import UserProfileSerializer, UserDetailSerializer 

from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser] 

    def get(self, request):
        user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

        profile_data = request.data.copy()  
        
        if request.content_type == "application/json":
            profile_data.pop("profile_image", None) 

        profile_serializer = UserProfileSerializer(
            user_profile,
            data=profile_data,
            partial=True
        )

        user_serializer = UserDetailSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        if profile_serializer.is_valid() and user_serializer.is_valid():
            profile_serializer.save()
            user_serializer.save()
            return Response(user_serializer.data, status=status.HTTP_200_OK)

        return Response({
            "profile_errors": profile_serializer.errors,
            "user_errors": user_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



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

class FCMDeviceViewSet(ModelViewSet):
    serializer_class = FCMDeviceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FCMDevice.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SendNotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user_id = request.data.get('user_id')
            title = request.data.get('title')
            body = request.data.get('body')
            data = request.data.get('data', {})

            if not all([user_id, title, body]):
                return Response(
                    {'error': 'Missing required fields'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            devices = FCMDevice.objects.filter(user_id=user_id)
            if not devices.exists():
                return Response(
                    {'error': 'No devices found for user'},
                    status=status.HTTP_404_NOT_FOUND
                )

            tokens = [device.token for device in devices]
            message = messaging.MulticastMessage(
                tokens=tokens,
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data
            )

            response = messaging.send_multicast(message)
            return Response({
                'success': True,
                'success_count': response.success_count,
                'failure_count': response.failure_count
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
