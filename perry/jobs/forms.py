from django import forms
from django.contrib.auth import get_user_model

from .models import Job

User = get_user_model()

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            "customer",
            "assigned_cleaner",
            "job_type",
            "description",
            "estimated_time",
            "price",
            "status",
            "scheduled_date",
            "scheduled_start_time",
            "scheduled_end_time",
            "completion_date",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing + " form-control").strip()


class JobImportForm(forms.Form):
    csv_file = forms.FileField(label="CSV file", help_text="Upload a CSV containing jobs to create or update.")


class JobAssignCleanerForm(forms.Form):
    cleaner = forms.ModelChoiceField(
        queryset=User.objects.filter(role__in=["CLEANER", "BOTH"]).order_by("last_name", "first_name"),
        required=True,
        label="Cleaner",
    )

    def __init__(self, *args, request_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if request_user is not None and getattr(request_user, "role", None) in {"CLEANER", "BOTH"}:
            self.fields["cleaner"].queryset = User.objects.filter(pk=request_user.pk)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing + " form-control").strip()
