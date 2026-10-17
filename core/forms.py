
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import EmployeeProfile,LeaveRequest, Task, Handover
from datetime import date


class EmployeeSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    employee_id = forms.CharField(max_length=30)
    department = forms.CharField(max_length=100)
    job_title = forms.CharField(max_length=100, required=False)
    phone = forms.CharField(max_length=20, required=False)
    date_of_joining = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    class Meta:
        model = get_user_model()
        fields = ("username", "email")

    def clean_employee_id(self):
        employee_id = self.cleaned_data["employee_id"].strip()

        if EmployeeProfile.objects.filter(
            employee_id__iexact=employee_id
        ).exists():
            raise forms.ValidationError(
                "This employee ID is already registered."
            )

        return employee_id


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = [
            "start_date",
            "end_date",
            "leave_type",
            "reason",
        ]
        widgets = {
            "start_date": forms.DateInput(
                attrs={"type": "date"}
            ),
            "end_date": forms.DateInput(
                attrs={"type": "date"}
            ),
            "reason": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Explain the reason for leave",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and start_date < date.today():
            self.add_error(
                "start_date",
                "Leave cannot start in the past.",
            )

        if start_date and end_date and end_date < start_date:
            self.add_error(
                "end_date",
                "End date cannot be before start date.",
            )

        return cleaned_data


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "due_date",
            "priority",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "e.g. Prepare monthly report",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Describe the task and next steps",
                }
            ),
            "due_date": forms.DateInput(
                attrs={"type": "date"}
            ),
        }

    def clean_title(self):
        title = self.cleaned_data["title"].strip()

        if not title:
            raise forms.ValidationError(
                "Please enter a task title."
            )

        return title


class HandoverForm(forms.ModelForm):
    class Meta:
        model = Handover
        fields = [
            "leave_request",
            "task",
            "backup_employee",
            "notes",
        ]
        widgets = {
            "notes": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": (
                        "Explain the current status, next steps, "
                        "and important instructions..."
                    ),
                }
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Default to no choices until a logged-in user is supplied.
        self.fields["leave_request"].queryset = LeaveRequest.objects.none()
        self.fields["task"].queryset = Task.objects.none()

        User = self._meta.model._meta.get_field(
            "backup_employee"
        ).remote_field.model

        self.fields["backup_employee"].queryset = User.objects.none()

        if user and user.is_authenticated:
            self.fields["leave_request"].queryset = (
                LeaveRequest.objects.filter(
                    employee=user,
                    status__in=[
                        LeaveRequest.Status.PENDING,
                        LeaveRequest.Status.APPROVED,
                    ],
                ).order_by("-created_at")
            )

            self.fields["task"].queryset = (
                Task.objects.filter(owner=user)
                .exclude(status=Task.Status.COMPLETED)
                .order_by("due_date", "title")
            )

            self.fields["backup_employee"].queryset = (
                User.objects.filter(is_active=True)
                .exclude(pk=user.pk)
                .order_by("username")
            )

        self.fields["leave_request"].empty_label = "Select your leave request"
        self.fields["task"].empty_label = "Select an unfinished task"
        self.fields["backup_employee"].empty_label = "Select a backup employee"
