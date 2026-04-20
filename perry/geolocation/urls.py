from django.urls import path

from .views import api_geocode, house_create, map_view

urlpatterns = [
    path("", map_view, name="map"),
    path("house/new/", house_create, name="house_create"),
    path("api/geocode/", api_geocode, name="api_geocode"),
]

