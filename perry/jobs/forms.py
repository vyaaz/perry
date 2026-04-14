from django import forms

from .models import Job


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
