from django.urls import path

from .views import invoice_create, invoice_list

urlpatterns = [
    path("", invoice_list, name="invoice_list"),
    path("new/", invoice_create, name="invoice_create"),
]

