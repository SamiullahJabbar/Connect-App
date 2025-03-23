from rest_framework import serializers
from .models import Job,JobApplication,Notification

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'company_name', 'city', 'job_type', 'salary', 'status', 'posted_by', 'created_at']
        read_only_fields = ['posted_by', 'created_at']




class JobApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.ReadOnlyField(source="job.title")
    company_name = serializers.ReadOnlyField(source="job.company_name")

    class Meta:
        model = JobApplication
        fields = ['id', 'job', 'job_title', 'company_name', 'status', 'completion_status', 'completion_image', 'applied_at', "user"]
        read_only_fields = ['status', 'applied_at']



class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at']