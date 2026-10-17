from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q


class EmployeeProfile(models.Model):
    # One profile per Django user account.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee_profile",
    )

    employee_id = models.CharField(
        max_length=30,
        unique=True,
    )
    department = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_joining = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["employee_id"]
        indexes = [
            models.Index(
                fields=["department"],
                name="profile_department_idx",
            ),
        ]

    def __str__(self):
        return f"{self.employee_id} - {self.user.username}"


class LeaveRequest(models.Model):
    class LeaveType(models.TextChoices):
        ANNUAL = "annual", "Annual Leave"
        SICK = "sick", "Sick Leave"
        PERSONAL = "personal", "Personal Leave"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="leave_requests",
    )
    start_date = models.DateField()
    end_date = models.DateField()

    leave_type = models.CharField(
        max_length=20,
        choices=LeaveType.choices,
        default=LeaveType.ANNUAL,
    )
    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_leave_requests",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    decision_note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(end_date__gte=F("start_date")),
                name="leave_end_after_start",
            ),
        ]
        indexes = [
            models.Index(
                fields=["status", "start_date"],
                name="leave_status_start_idx",
            ),
            models.Index(
                fields=["employee", "status"],
                name="leave_emp_status_idx",
            ),
            models.Index(
                fields=["employee", "-created_at"],
                name="leave_emp_created_idx",
            ),
        ]

    def clean(self):
        super().clean()

        if (
            self.start_date
            and self.end_date
            and self.end_date < self.start_date
        ):
            raise ValidationError({
                "end_date": "End date cannot be before start date."
            })

    def __str__(self):
        return f"Leave #{self.pk} - {self.get_status_display()}"


class Task(models.Model):
    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="owned_tasks",
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)

    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_date", "title"]
        indexes = [
            models.Index(
                fields=["owner", "status"],
                name="task_owner_status_idx",
            ),
            models.Index(
                fields=["status", "due_date"],
                name="task_status_due_idx",
            ),
        ]

    def __str__(self):
        return self.title


class Handover(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"

    leave_request = models.ForeignKey(
        LeaveRequest,
        on_delete=models.CASCADE,
        related_name="handovers",
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.PROTECT,
        related_name="handovers",
    )
    backup_employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="received_handovers",
    )

    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    accepted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["leave_request", "task"],
                name="unique_leave_task_handover",
            ),
        ]
        indexes = [
            models.Index(
                fields=["status", "created_at"],
                name="handover_status_created_idx",
            ),
            models.Index(
                fields=["backup_employee", "status"],
                name="handover_backup_status_idx",
            ),
        ]

    def clean(self):
        super().clean()

        if (
            self.leave_request_id
            and self.task_id
            and self.backup_employee_id
        ):
            leave = self.leave_request
            task = self.task

            if (
                leave.employee_id
                and task.owner_id
                and leave.employee_id != task.owner_id
            ):
                raise ValidationError(
                    "The task owner must be the employee requesting leave."
                )

            if self.backup_employee_id == leave.employee_id:
                raise ValidationError(
                    "An employee cannot be their own backup."
                )

    def __str__(self):
        return f"Handover #{self.pk} - {self.get_status_display()}"
