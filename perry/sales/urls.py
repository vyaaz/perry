from django.urls import path

from .views import sales_list

urlpatterns = [
    path("", sales_list, name="sales_list"),
]

