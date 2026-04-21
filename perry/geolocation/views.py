import json
import urllib.parse
import urllib.request

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import House
from .forms import HouseCreateForm, HouseUpdateForm


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


@login_required
def house_create(request):
    initial = {}
    try:
        if request.GET.get("lat"):
            initial["latitude"] = float(request.GET.get("lat"))
        if request.GET.get("lng"):
            initial["longitude"] = float(request.GET.get("lng"))
    except ValueError:
        pass
    if request.GET.get("address"):
        initial["address"] = request.GET.get("address")

    if request.method == "POST":
        form = HouseCreateForm(request.POST)
        if form.is_valid():
            house = form.save(commit=False)
            house.created_by = request.user
            house.save()
            messages.success(request, "House created.")
            return redirect("map")
    else:
        form = HouseCreateForm(initial=initial)

    return render(request, "geolocation/house_form.html", {"form": form})


@login_required
def house_edit(request, pk: int):
    house = get_object_or_404(House, pk=pk)

    if request.method == "POST":
        form = HouseUpdateForm(request.POST, instance=house)
        if form.is_valid():
            form.save()
            messages.success(request, "House updated.")
            return redirect("map")
    else:
        form = HouseUpdateForm(instance=house)

    return render(request, "geolocation/house_edit.html", {"form": form, "house": house})


@login_required
@require_GET
def api_geocode(request):
    """
    Lightweight geocoding proxy for address autocomplete.
    Uses OpenStreetMap Nominatim to return a list of suggestions.
    """
    q = (request.GET.get("q") or "").strip()
    if len(q) < 3:
        return JsonResponse({"results": []})

    params = {
        "q": q,
        "format": "jsonv2",
        "addressdetails": 1,
        "limit": 6,
    }
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(
        url,
        headers={
            # Nominatim usage policy asks for a descriptive UA
            "User-Agent": "PerryCRM/1.0 (address-autocomplete)",
            "Accept": "application/json",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            raw = resp.read().decode("utf-8")
            data = json.loads(raw)
    except Exception:
        return JsonResponse({"results": []})

    results = []
    for item in data:
        try:
            results.append(
                {
                    "display_name": item.get("display_name") or "",
                    "lat": float(item.get("lat")),
                    "lon": float(item.get("lon")),
                }
            )
        except Exception:
            continue

    return JsonResponse({"results": results})
