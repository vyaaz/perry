from django.contrib import admin

from .models import Sale, SalesEntry


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "customer", "house", "status", "open_day", "created_at")
    list_filter = ("status", "created_at", "user")
    search_fields = ("customer__first_name", "customer__last_name", "house__address", "user__username")
    autocomplete_fields = ("user", "customer", "house")
    readonly_fields = ("created_at", "updated_at")


@admin.register(SalesEntry)
class SalesEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "doors_knocked", "houses_sold", "closing_ratio")
    list_filter = ("date", "user")
    search_fields = ("user__username", "user__first_name", "user__last_name")
    autocomplete_fields = ("user",)

