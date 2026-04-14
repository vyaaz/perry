from django.contrib import admin

from .models import CalendarBlock


@admin.register(CalendarBlock)
class CalendarBlockAdmin(admin.ModelAdmin):
    list_display = ("job", "start_time", "end_time", "assigned_user")
    list_filter = ("assigned_user",)
    search_fields = ("job__customer__first_name", "job__customer__last_name", "job__description")
    autocomplete_fields = ("job", "assigned_user")
