from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, CommissionBracket


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


@admin.register(CommissionBracket)
class CommissionBracketAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "job", "sale", "commission_percentage", "commission_amount", "created_at")
    list_filter = ("role", "created_at")
    search_fields = ("user__username", "user__first_name", "user__last_name")
    autocomplete_fields = ("user", "job", "sale")

