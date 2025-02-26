from django.core.mail import send_mail

def send_job_application_notification(user_email, message):
    """Send an email to the user when their application status is updated."""
    subject = "Job Application Update"
    send_mail(
        subject,
        message,
        "your-email@gmail.com",  # Change to DEFAULT_FROM_EMAIL
        [user_email],
        fail_silently=False,
    )
