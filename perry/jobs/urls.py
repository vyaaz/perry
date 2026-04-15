from django.urls import path

from .views import add_customer_to_map, job_create, job_detail, job_list

urlpatterns = [
    path("", job_list, name="job_list"),
    path("new/", job_create, name="job_create"),
    path("<int:pk>/", job_detail, name="job_detail"),
    path("<int:pk>/add-to-map/", add_customer_to_map, name="add_customer_to_map"),
]

