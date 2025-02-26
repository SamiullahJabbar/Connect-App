from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def custom_admin_dashboard(request):
    from .models import Job, JobApplication, Notification, User 
    total_jobs = Job.objects.count()
    total_applications = JobApplication.objects.count()
    total_users = User.objects.count()
    total_notifications = Notification.objects.filter(is_read=False).count()

    context = {
        "total_jobs": total_jobs,
        "total_applications": total_applications,
        "total_users": total_users,
        "total_notifications": total_notifications,
    }
    return render(request, "admin/custom_dashboard.html", context)
