
from django.core.mail import send_mail
from django.conf import settings

from firebase_admin import messaging

def send_job_application_notification(user_email, job_title, status):
    """Send an email notification to the user when their job status is updated."""
    subject = f"Job '{job_title}' Status Update"
    
    if status == "approved":
        message = f"Congratulations! Your job post '{job_title}' has been approved by the admin."
    elif status == "rejected":
        message = f"Sorry! Your job post '{job_title}' has been rejected by the admin."
    else:
        message = f"Your job post '{job_title}' status has been updated to '{status}'."
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,  # Now using DEFAULT_FROM_EMAIL
            [user_email],
            fail_silently=False,
        )
    except Exception as e:
        print("Error sending email:", e)
        return False


def send_application_notification(job_owner_email, applicant_name, job_title):
    """Notify job owner when someone applies for their job."""
    subject = "New Job Application Received"
    message = f"Hi,\n\n{applicant_name} has applied for your job post: '{job_title}'. Please review and approve/reject the application."
    
    try:
        send_mail(
        subject,
        message,
            "your-email@gmail.com",  # Change to your email
            [job_owner_email],
            fail_silently=False,
        )
    except Exception as e:
        print("Error sending email:", e)
        return False


def send_application_status_email(user_email, job_title, status):
    """Send an email to the user when their job application is approved/rejected."""
    subject = "Job Application Status Update"
    
    if status == "approved":
        message = f"Congratulations! Your job application for '{job_title}' has been approved."
    else:
        message = f"Unfortunately, your job application for '{job_title}' has been rejected."

    try:
        send_mail(
            subject,
            message,
            "your-email@gmail.com",  # Change to your DEFAULT_FROM_EMAIL
            [user_email],
            fail_silently=False,
        )
    except Exception as e:
        print("Error sending email:", e)
        return False



def send_job_completion_email(job_owner_email, job_owner_name, applicant_name, job_title):
    """Send an email to the job owner when a job is marked as completed"""
    subject = "Job Completion Notification"
    message = f"""
    Hello {job_owner_name},

    The user {applicant_name} has marked the job '{job_title}' as completed.
    Please review the proof of completion and confirm the completion status.

    Best regards,
    Job Platform Team
    """
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [job_owner_email], fail_silently=False)
    except Exception as e:
        print("Error sending email:", e)
        return False


def send_push_notification(fcm_token, title, body):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        token=fcm_token
    )
    response = messaging.send(message)
    return response
