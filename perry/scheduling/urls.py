from django.urls import path

from .views import api_job_move, api_jobs, schedule_list

urlpatterns = [
    path("", schedule_list, name="schedule_list"),
    path("api/jobs/", api_jobs, name="api_jobs"),
    path("api/jobs/<int:pk>/move/", api_job_move, name="api_job_move"),
]

