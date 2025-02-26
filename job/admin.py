from django.contrib import admin
from .models import Job, JobApplication, Notification


class JobAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "company_name", "city", "job_type", "salary", "status", "posted_by", "created_at")
    list_filter = ("status", "city", "job_type", "salary", "created_at")
    search_fields = ("title", "company_name", "city", "posted_by__username")
    ordering = ("-created_at",)


class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "job", "status", "completion_status", "applied_at")
    list_filter = ("status", "completion_status")
    search_fields = ("user__username", "job__title")

    actions = ["approve_applications", "reject_applications"]

    def approve_applications(self, request, queryset):
        queryset.update(status="approved")
    approve_applications.short_description = "Approve selected applications"

    def reject_applications(self, request, queryset):
        queryset.update(status="rejected")
    reject_applications.short_description = "Reject selected applications"




class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "message", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__username", "message")
    ordering = ("-created_at",)


admin.site.register(Job, JobAdmin)
admin.site.register(JobApplication, JobApplicationAdmin)
admin.site.register(Notification, NotificationAdmin)
