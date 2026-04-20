from django.urls import path

from .views import invoice_create, invoice_list, invoice_toggle_paid

urlpatterns = [
    path("", invoice_list, name="invoice_list"),
    path("new/", invoice_create, name="invoice_create"),
    path("<int:pk>/toggle-paid/", invoice_toggle_paid, name="invoice_toggle_paid"),
]

