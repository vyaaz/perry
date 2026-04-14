from django.urls import path

from .views import schedule_list

urlpatterns = [
    path("", schedule_list, name="schedule_list"),
]

