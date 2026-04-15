from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import House


@login_required
def map_view(request):
    houses = House.objects.all()[:500]
    houses_data = [
        {
            "id": house.id,
            "address": house.address,
            "latitude": float(house.latitude),
            "longitude": float(house.longitude),
            "status": house.status,
            "status_display": house.get_status_display(),
        }
        for house in houses
    ]
    return render(request, "geolocation/map.html", {"houses": houses_data})
