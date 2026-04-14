from django.contrib import admin

from .models import SalesEntry


@admin.register(SalesEntry)
class SalesEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "doors_knocked", "houses_sold", "closing_ratio")
    list_filter = ("date", "user")
    search_fields = ("user__username", "user__first_name", "user__last_name")
    autocomplete_fields = ("user",)
