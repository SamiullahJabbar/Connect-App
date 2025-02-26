import re
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .utils import send_verification_email
from .models import UserProfile,ChatMessage

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True, min_length=8, error_messages={
        "min_length": "Password must be at least 8 characters long."
    })

    class Meta:
        model = User
        fields = ['email', 'username', 'phone_number', 'password']

    def validate_phone_number(self, value):
        """Ensure phone number includes country code"""
        phone_regex = r'^\+?[1-9]\d{1,14}$'  # Regex to validate phone number with country code
        if not re.match(phone_regex, value):
            raise serializers.ValidationError("Invalid phone number format. Include country code.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password']
        )
        send_verification_email(user)
        return user



class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'phone_number', 'is_verified']




class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['skills', 'experience', 'city', 'education', 'about_me']

class UserDetailSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'phone_number', 'is_verified', 'profile']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        if profile_data:
            UserProfile.objects.update_or_create(user=instance, defaults=profile_data)
        return super().update(instance, validated_data)
    


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source="sender.username")
    receiver = serializers.ReadOnlyField(source="receiver.username")

    class Meta:
        model = ChatMessage
        fields = ["id", "sender", "receiver", "message", "timestamp"]
