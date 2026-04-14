from django.contrib import admin

from .models import Invoice, WorkerPayment


class WorkerPaymentInline(admin.TabularInline):
    model = WorkerPayment
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "job", "amount", "paid", "completion_date", "created_at")
    list_filter = ("paid", "created_at", "completion_date")
    search_fields = ("customer__first_name", "customer__last_name", "job__description")
    autocomplete_fields = ("customer", "job")
    inlines = [WorkerPaymentInline]


@admin.register(WorkerPayment)
class WorkerPaymentAdmin(admin.ModelAdmin):
    list_display = ("invoice", "user", "role", "amount")
    list_filter = ("role",)
    search_fields = ("invoice__customer__first_name", "invoice__customer__last_name", "user__username")
    autocomplete_fields = ("invoice", "user")
