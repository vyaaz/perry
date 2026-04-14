from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "commission_tier",
        "is_active",
        "is_staff",
    )
    list_filter = ("role", "commission_tier", "is_active", "is_staff", "is_superuser")
    search_fields = ("username", "email", "first_name", "last_name", "phone_number")
    ordering = ("username",)

    fieldsets = UserAdmin.fieldsets + (
        ("CRM Fields", {"fields": ("phone_number", "role", "commission_tier", "hire_date")}),
    )
