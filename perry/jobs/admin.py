from django.contrib import admin

from .models import Job, JobCleaner


class JobCleanerInline(admin.TabularInline):
    model = JobCleaner
    extra = 0


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
    autocomplete_fields = ("customer", "created_by", "assigned_cleaner", "sale")
    inlines = [JobCleanerInline]


@admin.register(JobCleaner)
class JobCleanerAdmin(admin.ModelAdmin):
    list_display = ("job", "cleaner", "assigned_at")
    list_filter = ("assigned_at",)
    search_fields = ("job__customer__first_name", "cleaner__username")
    autocomplete_fields = ("job", "cleaner")

