from django.urls import path

from .views import (
    add_customer_to_map,
    job_assign_cleaner,
    job_create,
    job_detail,
    job_import,
    job_list,
    job_mark_complete,
)

urlpatterns = [
    path("", job_list, name="job_list"),
    path("new/", job_create, name="job_create"),
    path("import/", job_import, name="job_import"),
    path("<int:pk>/", job_detail, name="job_detail"),
    path("<int:pk>/assign-cleaner/", job_assign_cleaner, name="job_assign_cleaner"),
    path("<int:pk>/complete/", job_mark_complete, name="job_mark_complete"),
    path("<int:pk>/add-to-map/", add_customer_to_map, name="add_customer_to_map"),
]

