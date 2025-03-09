from django.urls import path
from .views import JobView, ApprovedJobSearchView,JobApplicationView,JobApplicationApprovalView,NotificationView,JobCompletionView,JobPosterCompletionView,AdminJobApprovalView,AllAdminJobListView

urlpatterns = [
    path('search-job/', ApprovedJobSearchView.as_view(), name='job-list'),  
    path('admin/jobs/', JobView.as_view(), name='job-create'), 
    path('admin/pending-jobs/', AdminJobApprovalView.as_view(), name='admin-pending-jobs'),  
    path('admin/job-approval/<int:job_id>/', AdminJobApprovalView.as_view(), name='admin-job-approval'), 
    path('get-job-applications/', JobApplicationApprovalView.as_view(), name="job-applications"),
    path('job-applications/<int:application_id>/', JobApplicationApprovalView.as_view(), name="approve-application"),
    path('admin/jobs/<int:job_id>/', JobView.as_view(), name='job-update-delete'), 
    path('jobs/<int:job_id>/apply/', JobApplicationView.as_view(), name='apply-job'),
    path('applications/', JobApplicationView.as_view(), name='user-applications'),
    path('notifications/', NotificationView.as_view(), name='user-notifications'),
    path('notifications/<int:notification_id>/', NotificationView.as_view(), name='mark-notification-read'),
    path('jobs/<int:application_id>/complete/', JobCompletionView.as_view(), name='job-completion'),
    path('jobs/completed/', JobCompletionView.as_view(), name='job-completed-list'),
    path('owner/jobs/<int:application_id>/confirm/', JobPosterCompletionView.as_view(), name='admin-job-confirmation'),
    path('Adminalljob/', AllAdminJobListView.as_view(), name='job-completed-list'),
]
