from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.timezone import now
from datetime import timedelta
from .models import User

def send_verification_email(user):
    """Send an email with OTP to verify the user"""
    user.generate_otp()  # Generate OTP before sending

    subject = "Your Email Verification Code"
    context = {"user": user, "otp": user.otp}
    html_message = render_to_string("email_verification.html", context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        "your-email@gmail.com",  # Change to DEFAULT_FROM_EMAIL
        [user.email],
        html_message=html_message,
    )
