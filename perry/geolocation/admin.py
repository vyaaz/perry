from django.contrib import admin

from .models import House


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ("address", "status", "latitude", "longitude", "created_by", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("address", "created_by__username", "created_by__first_name", "created_by__last_name")
    autocomplete_fields = ("created_by",)
