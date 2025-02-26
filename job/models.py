from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Job(models.Model):
    JOB_STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    company_name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    job_type = models.CharField(max_length=100)  # Full-time, Part-time, Remote
    salary = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=JOB_STATUS_CHOICES, default='open')
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


def job_completion_upload_path(instance, filename):
    """Defines where job completion images are stored"""
    return f'job_completions/{instance.user.id}/{filename}'

class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    COMPLETION_STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    completion_status = models.CharField(max_length=15, choices=COMPLETION_STATUS_CHOICES, default='not_started')
    applied_at = models.DateTimeField(auto_now_add=True)
    completion_image = models.ImageField(upload_to=job_completion_upload_path, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} applied for {self.job.title} - {self.status}"



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    is_read = models.BooleanField(default=False)  # Mark as read/unread
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.message}"
