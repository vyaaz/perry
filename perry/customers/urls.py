from django.urls import path

from .views import add_customer_to_map, customer_create, customer_detail, customer_list

urlpatterns = [
    path("", customer_list, name="customer_list"),
    path("new/", customer_create, name="customer_create"),
    path("<int:pk>/", customer_detail, name="customer_detail"),
    path("<int:pk>/add-to-map/", add_customer_to_map, name="add_customer_to_map"),
]

