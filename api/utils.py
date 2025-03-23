from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.timezone import now
from datetime import timedelta
from .models import User
from jobportal.settings import DEFAULT_FROM_EMAIL

def send_verification_email(user):
    """Send an email with OTP to verify the user"""
    user.generate_otp()  # Generate OTP before sending

    subject = "Your Email Verification Code"
    context = {"user": user, "otp": user.otp}
    html_message = render_to_string("email_verification.html", context)
    plain_message = strip_tags(html_message)

    try:
        send_mail(
            subject,
            plain_message,
            DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
        )
    except Exception as e:
        print("error",e)
        return False
