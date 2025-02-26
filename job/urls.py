from django.urls import path
from .views import JobAdminView, JobListView,JobApplicationView,AdminJobApplicationView,NotificationView,JobCompletionView,AdminJobCompletionView

urlpatterns = [
    path('jobs/', JobListView.as_view(), name='job-list'),  
    path('admin/jobs/', JobAdminView.as_view(), name='job-create'), 
    path('admin/jobs/<int:job_id>/', JobAdminView.as_view(), name='job-update-delete'), 
    path('jobs/<int:job_id>/apply/', JobApplicationView.as_view(), name='apply-job'),
    path('applications/', JobApplicationView.as_view(), name='user-applications'),
    path('admin/applications/', AdminJobApplicationView.as_view(), name='admin-applications'),
    path('admin/applications/<int:application_id>/', AdminJobApplicationView.as_view(), name='admin-application-update'),
    path('notifications/', NotificationView.as_view(), name='user-notifications'),
    path('notifications/<int:notification_id>/', NotificationView.as_view(), name='mark-notification-read'),
    path('jobs/<int:application_id>/complete/', JobCompletionView.as_view(), name='job-completion'),
    path('admin/jobs/<int:application_id>/confirm/', AdminJobCompletionView.as_view(), name='admin-job-confirmation'),
]
