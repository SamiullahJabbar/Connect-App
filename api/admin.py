from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile, ChatMessage

admin.site.site_header = "Connect pay"
admin.site.site_title = "Connect pay"
admin.site.index_title = "Welcome"




from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, ChatMessage


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("id", "email", "username", "phone_number", "is_verified", "is_staff", "is_superuser")
    list_filter = ("is_verified", "is_staff", "is_superuser")
    search_fields = ("email", "username", "phone_number")
    ordering = ("id",)

    fieldsets = (
        ("User Info", {"fields": ("email", "username", "phone_number", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_superuser", "is_verified")}),
        ("Security", {"fields": ("otp", "otp_created_at")}),
    )
    
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "phone_number", "password1", "password2"),
        }),
    )


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "city", "education", "experience")
    list_filter = ("city", "education")
    search_fields = ("user__email", "user__username", "city")
    ordering = ("id",)


class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "receiver", "timestamp")
    list_filter = ("timestamp",)
    search_fields = ("sender__username", "receiver__username", "message")
    ordering = ("id",)


admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)
