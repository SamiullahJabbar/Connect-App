import random
import string
from datetime import datetime, timedelta
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, username, phone_number, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        if not username:
            raise ValueError("The Username field must be set")
        if not phone_number:
            raise ValueError("The Phone Number field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, phone_number, password, **extra_fields)

class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True, default="default_username")
    email = models.EmailField(unique=True) 
    phone_number = models.CharField(max_length=15, null=True, blank=True)  
    is_verified = models.BooleanField(default=False) 
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_number'] 

    objects = UserManager()

    def __str__(self):
        return self.email

    def generate_otp(self):
        """Generate a 6-digit OTP"""
        self.otp = ''.join(random.choices(string.digits, k=6))
        self.otp_created_at = now()
        self.save()



def user_profile_image_path(instance, filename):
    """Generate file path for new user profile image."""
    return f'profile_images/{instance.user.id}/{filename}'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_image = models.ImageField(upload_to=user_profile_image_path, blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    experience = models.PositiveIntegerField(default=0)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)  # Added address field
    education = models.CharField(max_length=255, blank=True, null=True)
    about_me = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"





class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} to {self.receiver.username}: {self.message}"
