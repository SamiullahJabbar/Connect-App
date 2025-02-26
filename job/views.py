from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import JobSerializer,JobApplicationSerializer,NotificationSerializer
from .models import Job,JobApplication,Notification
from .utils import send_job_application_notification
from rest_framework.parsers import MultiPartParser, FormParser

# Admin Job Management (Create, Update, Delete)
class JobAdminView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = JobSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(posted_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, job_id):
        try:
            job = Job.objects.get(id=job_id, posted_by=request.user)
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = JobSerializer(job, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, job_id):
        try:
            job = Job.objects.get(id=job_id, posted_by=request.user)
            job.delete()
            return Response({"message": "Job deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

# Public Job Listing
class JobListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        city = request.query_params.get('city')
        job_type = request.query_params.get('job_type')

        jobs = Job.objects.filter(status='open')

        if city:
            jobs = jobs.filter(city__iexact=city)
        if job_type:
            jobs = jobs.filter(job_type__iexact=job_type)

        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)





class JobApplicationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, job_id):
        user = request.user
        try:
            job = Job.objects.get(id=job_id, status="open")
        except Job.DoesNotExist:
            return Response({"error": "Job not found or closed"}, status=status.HTTP_404_NOT_FOUND)

        # Check if user has already applied
        if JobApplication.objects.filter(user=user, job=job).exists():
            return Response({"error": "You have already applied for this job"}, status=status.HTTP_400_BAD_REQUEST)

        # Apply for job
        application = JobApplication.objects.create(user=user, job=job)
        serializer = JobApplicationSerializer(application)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        applications = JobApplication.objects.filter(user=request.user)
        serializer = JobApplicationSerializer(applications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Admin Approves/Rejects Applications
class AdminJobApplicationView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        applications = JobApplication.objects.all()
        serializer = JobApplicationSerializer(applications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, application_id):
        try:
            application = JobApplication.objects.get(id=application_id)
        except JobApplication.DoesNotExist:
            return Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("status")
        if new_status not in ['approved', 'rejected']:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        application.status = new_status
        application.save()
        return Response({"message": f"Application status updated to {new_status}"}, status=status.HTTP_200_OK)
    





class AdminJobApplicationView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, application_id):
        try:
            application = JobApplication.objects.get(id=application_id)
        except JobApplication.DoesNotExist:
            return Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("status")
        if new_status not in ['approved', 'rejected']:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        application.status = new_status
        application.save()

        # Send Notification
        message = f"Your job application for {application.job.title} has been {new_status}."
        Notification.objects.create(user=application.user, message=message)

        # Send Email
        send_job_application_notification(application.user.email, message)

        return Response({"message": f"Application status updated to {new_status}"}, status=status.HTTP_200_OK)
    




class NotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({"message": "Notification marked as read"}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)


class JobCompletionView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)  # Allows image upload

    def put(self, request, application_id):
        try:
            application = JobApplication.objects.get(id=application_id, user=request.user)
        except JobApplication.DoesNotExist:
            return Response({"error": "Job application not found"}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("completion_status")
        completion_image = request.FILES.get("completion_image")  # Get uploaded image

        if new_status not in ['in_progress', 'completed']:
            return Response({"error": "Invalid completion status"}, status=status.HTTP_400_BAD_REQUEST)

        if application.completion_status == "not_started" and new_status == "in_progress":
            application.completion_status = "in_progress"
            application.save()
            return Response({"message": "Job started successfully"}, status=status.HTTP_200_OK)

        if application.completion_status == "in_progress" and new_status == "completed":
            if not completion_image:
                return Response({"error": "Completion image is required"}, status=status.HTTP_400_BAD_REQUEST)

            application.completion_status = "completed"
            application.completion_image = completion_image  # Save image
            application.save()

            # Notify Admin
            message = f"{request.user.username} has marked the job '{application.job.title}' as completed. Please confirm."
            Notification.objects.create(user=application.job.posted_by, message=message)

            return Response({"message": "Job marked as completed with proof, waiting for admin confirmation"}, status=status.HTTP_200_OK)

        return Response({"error": "Job cannot be updated to this status"}, status=status.HTTP_400_BAD_REQUEST)

# ✅ Admin Confirms or Rejects Job Completion
class AdminJobCompletionView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, application_id):
        try:
            application = JobApplication.objects.get(id=application_id, completion_status="completed")
        except JobApplication.DoesNotExist:
            return Response({"error": "No completed job found for confirmation"}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("completion_status")

        if new_status not in ['confirmed', 'rejected']:
            return Response({"error": "Invalid completion status"}, status=status.HTTP_400_BAD_REQUEST)

        application.completion_status = new_status
        application.save()

        # Notify User
        if new_status == "confirmed":
            message = f"Your job '{application.job.title}' completion has been confirmed by the admin."
        else:
            message = f"Your job '{application.job.title}' completion was rejected by the admin."

        Notification.objects.create(user=application.user, message=message)
        send_job_application_notification(application.user.email, message)

        return Response({"message": f"Job completion status updated to {new_status}"}, status=status.HTTP_200_OK)