from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import House


@login_required
def map_view(request):
    houses = House.objects.all()[:500]
    return render(request, "geolocation/map.html", {"houses": houses})
