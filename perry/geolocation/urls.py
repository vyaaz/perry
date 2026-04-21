from django.urls import path

from .views import api_geocode, house_edit, map_view

urlpatterns = [
    path("", map_view, name="map"),
    path("house/<int:pk>/edit/", house_edit, name="house_edit"),
    path("api/geocode/", api_geocode, name="api_geocode"),
]

