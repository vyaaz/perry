from django.contrib import admin

from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "job_type",
        "status",
        "scheduled_date",
        "assigned_cleaner",
        "price",
        "created_at",
    )
    list_filter = ("job_type", "status", "scheduled_date", "created_at")
    search_fields = (
        "customer__first_name",
        "customer__last_name",
        "description",
    )
    autocomplete_fields = ("customer", "created_by", "assigned_cleaner")
