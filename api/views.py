from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserDetailSerializer,ChatMessageSerializer
from .models import UserProfile,ChatMessage




User = get_user_model()

class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]


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

from rest_framework.parsers import MultiPartParser, FormParser  

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  

    def get(self, request):
        user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

        profile_serializer = UserProfileSerializer(
            user_profile,
            data=request.data,
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
