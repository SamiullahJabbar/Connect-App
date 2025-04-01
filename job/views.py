from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import JobSerializer,JobApplicationSerializer,NotificationSerializer
from .models import Job,JobApplication,Notification
from .utils import send_job_application_notification,send_application_notification,send_application_status_email,send_job_completion_email 
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from django.contrib.auth import get_user_model
User = get_user_model()
from api.models import UserProfile
from .utils import send_push_notification
from api.models import FCMDevice


# user Job Management (Create, Update, Delete)
class JobView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Allow users to post a job (default status: pending)"""
        serializer = JobSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(posted_by=request.user, status="pending")  
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, job_id):
        """Allow users to update only their own jobs, admins can update any job"""
        try:
            print("job_id",job_id)
            job = Job.objects.get(id=job_id)
            if request.user != job.posted_by and not request.user.is_staff and not request.user.is_superuser:
                return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        except Job.DoesNotExist as e:
            print("error",e)
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = JobSerializer(job, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, job_id):
        """Allow users to delete only their own jobs, admins can delete any job"""
        try:
            job = Job.objects.get(id=job_id)
            if request.user != job.posted_by and not request.user.is_staff and not request.user.is_superuser:
                return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
            job.delete()
            return Response({"message": "Job deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request):
        """Retrieve all jobs posted by the logged-in user"""
        jobs = Job.objects.filter(posted_by=request.user)
        serializer = JobSerializer(jobs, many=True)
        for job in serializer.data:
            userProfile, _ = UserProfile.objects.get_or_create(user=job['posted_by'])
            job['company_logo'] = userProfile.profile_image.url if userProfile.profile_image else None
        return Response(serializer.data, status=status.HTTP_200_OK)

class AdminJobApprovalView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser] 
    def get(self, request):
        """Fetch all jobs that are pending approval"""
        pending_jobs = Job.objects.filter(status="pending")
        serializer = JobSerializer(pending_jobs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, job_id):
        """Admin approves or rejects a job"""
        try:
            job = Job.objects.get(id=job_id, status="pending")  
        except Job.DoesNotExist:
            return Response({"error": "Job not found or already processed"}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("status") 

        if new_status not in ["approved", "rejected"]:
            return Response({"error": "Invalid status. Use 'approved' or 'rejected'."}, status=status.HTTP_400_BAD_REQUEST)

        job.status = new_status
        job.save()

        # Notify User (In-App Notification)
        if new_status == "approved":
            message = f"Your job '{job.title}' has been approved by the admin."
        else:
            message = f"Your job '{job.title}' has been rejected by the admin."

        Notification.objects.create(user=job.posted_by, message=message)

        # Send Email Notification
        send_job_application_notification(job.posted_by.email, job.title, new_status)

        # send push notification
        try:
            try:
                # send notifications to all the devices of the job poster
                fcm_tokens = FCMDevice.objects.filter(user=job.posted_by)
                for fcm_token in fcm_tokens:
                    send_push_notification(fcm_token.token, "New Job Status", f"Your job '{job.title}' has been {new_status}.")
            except Exception as e:
                print("exception",e)
        except Exception as e:
            print("error",e)
        return Response({"message": f"Job status updated to {new_status}"}, status=status.HTTP_200_OK)



class ApprovedJobSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q", "").strip()  
        jobs = Job.objects.filter(status="approved") 

        if query:
            words = query.split()  
            search_filter = Q()
            for word in words:
                search_filter |= Q(city__icontains=word) | Q(title__icontains=word)

            jobs = jobs.filter(search_filter)
            

        serializer = JobSerializer(jobs, many=True)
        # add company_logo field to the serializer
        for job in serializer.data:
            userProfile, _ = UserProfile.objects.get_or_create(user=job['posted_by'])
            job['company_logo'] = userProfile.profile_image.url if userProfile.profile_image else None

        return Response(serializer.data, status=status.HTTP_200_OK)



class JobAppliedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve all jobs applied by the logged-in user"""
        applications = JobApplication.objects.filter(user=request.user)
        serializer = JobApplicationSerializer(applications, many=True)
        for application in serializer.data:
            creator_of_job = Job.objects.get(id=application['job'])
            profile_data, _ = UserProfile.objects.get_or_create(user=creator_of_job.posted_by)
            application['company_image'] = profile_data.profile_image.url if profile_data.profile_image else None
            
        return Response(serializer.data, status=status.HTTP_200_OK)

class JobToApproveView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve all jobs that are pending approval"""
        if request.user.is_superuser:
            jobs = Job.objects.filter(status="pending")
            serializer = JobSerializer(jobs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "You are not authorized to access this resource"}, status=status.HTTP_403_FORBIDDEN)


class JobApplicationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, job_id):
        user = request.user
        try:
            job = Job.objects.get(id=job_id, status="approved")
        except Job.DoesNotExist:
            return Response({"error": "Job not found or closed"}, status=status.HTTP_404_NOT_FOUND)

        if JobApplication.objects.filter(user=user, job=job).exists():
            return Response({"error": "You have already applied for this job"}, status=status.HTTP_202_ACCEPTED)
        application = JobApplication.objects.create(user=user, job=job, status="pending")
        send_application_notification(job.posted_by.email, user.username, job.title)
        Notification.objects.create(
            user=job.posted_by,
            message=f"{user.username} has applied for your job: {job.title}."
        )
        # send push notification
        try:
            try:
                fcm_tokens = FCMDevice.objects.filter(user=job.posted_by)
                for fcm_token in fcm_tokens:
                    send_push_notification(fcm_token.token, "New Job Application", f"{user.username} has applied for your job: {job.title}.")
            except Exception as e:
                print("exception",e)
        except Exception as e:
            print("error",e)

        serializer = JobApplicationSerializer(application)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, job_id):
        """Fetch all applications of the logged-in user"""
        applications = JobApplication.objects.filter(user=request.user, job=job_id)
        serializer = JobApplicationSerializer(applications, many=True)
        for application in serializer.data:
            userProfile, _ = UserProfile.objects.get_or_create(user=application['user'])
            application['user'] = {}
            application['user']['username'] = userProfile.user.username
            application['user']['profile_image'] = userProfile.profile_image.url if userProfile.profile_image else None
        return Response(serializer.data, status=status.HTTP_200_OK)

class JobApplicationApprovalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve all applications for jobs posted by the logged-in job owner"""
        user = request.user
        jobs_posted_by_user = Job.objects.filter(posted_by=user)
        print("jobs_posted_by_user",jobs_posted_by_user)
        applications = JobApplication.objects.filter(job__in=jobs_posted_by_user)  

        serializer = JobApplicationSerializer(applications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, application_id):
        """Job owner approves/rejects an application"""
        try:
            application = JobApplication.objects.get(id=application_id)
            if application.job.posted_by != request.user:
                return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        except JobApplication.DoesNotExist:
            return Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("status")  
        
        if new_status not in ['approved', 'rejected']:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        application.status = new_status
        application.save()
        send_application_status_email(application.user.email, application.job.title, new_status)

        if new_status == "approved":
            message = f"Your job application for '{application.job.title}' has been approved."
        else:
            message = f"Your job application for '{application.job.title}' has been rejected."

        Notification.objects.create(user=application.user, message=message)

        # send push notification
        try:
            try:
                fcm_tokens = FCMDevice.objects.filter(user=application.user)
                for fcm_token in fcm_tokens:
                    send_push_notification(fcm_token.token, "New Job Application", f"{application.user.username} has applied for your job: {application.job.title}.")
            except Exception as e:
                print("exception",e)
        except Exception as e:
            print("error",e)

        return Response({"message": f"Application status updated to {new_status}"}, status=status.HTTP_200_OK)


    



# class AdminJobApplicationView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def put(self, request, application_id):
#         try:
#             application = JobApplication.objects.get(id=application_id)
#         except JobApplication.DoesNotExist:
#             return Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)

#         new_status = request.data.get("status")
#         if new_status not in ['approved', 'rejected']:
#             return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

#         application.status = new_status
#         application.save()

#         # Send Notification
#         message = f"Your job application for {application.job.title} has been {new_status}."
#         Notification.objects.create(user=application.user, message=message)

#         # Send Email
#         send_job_application_notification(application.user.email, message)

#         return Response({"message": f"Application status updated to {new_status}"}, status=status.HTTP_200_OK)
    




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

from django.core.mail import send_mail

class JobCompletionView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)  

    def get(self, request):
        """Retrieve all confirmed job applications for jobs posted by the logged-in job owner"""
        user = request.user
        jobs_posted_by_user = Job.objects.filter(posted_by=user)
        if not jobs_posted_by_user.exists():
            return Response({"error": "You are not a job owner or have no posted jobs"}, status=status.HTTP_403_FORBIDDEN)
        confirmed_applications = JobApplication.objects.filter(
            job__in=jobs_posted_by_user, 
            completion_status="completed"
        )
        serializer = JobApplicationSerializer(confirmed_applications, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, application_id):
        try:
            application = JobApplication.objects.get(id=application_id, user=request.user)
        except JobApplication.DoesNotExist:
            return Response({"error": "Job application not found"}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("completion_status")
        completion_image = request.FILES.get("completion_image")  

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
            application.completion_image = completion_image 
            application.save()
            send_mail(
                subject="Job Completion Notification",
                message=f"Hello {application.job.posted_by.username},\n\n"
                        f"User {request.user.username} has completed the job '{application.job.title}'.\n"
                        "Please review and confirm the completion.",
                from_email="your-email@example.com",
                recipient_list=[application.job.posted_by.email],
                fail_silently=False,
            )
            Notification.objects.create(
                user=application.job.posted_by,
                message=f"{request.user.username} has marked the job '{application.job.title}' as completed. Please confirm."
            )
            
            # send push notification
            try:
                try:
                    fcm_tokens = FCMDevice.objects.filter(user=application.job.posted_by)
                    for fcm_token in fcm_tokens:
                        send_push_notification(fcm_token.token, "New Job Completion", f"{request.user.username} has marked the job '{application.job.title}' as completed. Please confirm.")
                except Exception as e:
                    print("exception",e)
            except Exception as e:
                print("error",e)

            return Response({"message": "Job marked as completed with proof, waiting for confirmation"}, status=status.HTTP_200_OK)

        return Response({"error": "Job cannot be updated to this status"}, status=status.HTTP_400_BAD_REQUEST)


class JobPosterCompletionView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, application_id):
        try:
            application = JobApplication.objects.select_related("job").get(
                id=application_id, completion_status="completed"
            )
            if request.user != application.job.posted_by:
                return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        except JobApplication.DoesNotExist:
            return Response({"error": "No completed job found for confirmation"}, status=status.HTTP_404_NOT_FOUND)
        new_status = request.data.get("completion_status")

        if new_status not in ['confirmed', 'rejected']:
            return Response({"error": "Invalid completion status"}, status=status.HTTP_400_BAD_REQUEST)
        application.completion_status = new_status
        application.save()
        if new_status == "confirmed":
            message = f"Your job '{application.job.title}' completion has been confirmed by the job owner."
        else:
            message = f"Your job '{application.job.title}' completion was rejected by the job owner."
        Notification.objects.create(user=application.user, message=message)
        send_job_application_notification(application.user.email, message, new_status)

        # send push notification
        try:
            try:
                fcm_tokens = FCMDevice.objects.filter(user=application.user)
                for fcm_token in fcm_tokens:
                    send_push_notification(fcm_token.token, "New Job Completion", f"{application.user.username} has marked the job '{application.job.title}' as completed. Please confirm.")
            except Exception as e:
                print("exception",e)
        except Exception as e:
            print("error",e)

        return Response({"message": f"Job completion status updated to {new_status}"}, status=status.HTTP_200_OK)





class AllAdminJobListView(APIView):
    permission_classes = [IsAdminUser]  

    def get(self, request):
        jobs = Job.objects.all() 
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)