
from django.contrib import admin
from .models import EmployeeProfile, LeaveRequest, Task, Handover


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = (
        "employee_id",
        "user",
        "department",
        "job_title",
        "date_of_joining",
    )
    search_fields = (
        "employee_id",
        "user__username",
        "user__email",
        "department",
    )
    list_filter = ("department",)


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "employee",
        "start_date",
        "end_date",
        "leave_type",
        "status",
        "reviewed_by",
        "created_at",
    )
    search_fields = (
        "employee__username",
        "reason",
        "decision_note",
    )
    list_filter = ("status", "leave_type", "start_date")
    readonly_fields = ("created_at", "reviewed_at")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "owner",
        "due_date",
        "priority",
        "status",
    )
    search_fields = ("title", "description", "owner__username")
    list_filter = ("status", "priority", "due_date")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Handover)
class HandoverAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "leave_request",
        "task",
        "backup_employee",
        "status",
        "accepted_at",
    )
    search_fields = (
        "task__title",
        "leave_request__employee__username",
        "backup_employee__username",
        "notes",
    )
    list_filter = ("status", "created_at")
    readonly_fields = ("created_at", "updated_at", "accepted_at")
