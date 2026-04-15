from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from accounts.permissions import role_required

from .forms import JobForm
from .models import Job


@login_required
def job_list(request):
    qs = Job.objects.select_related("customer", "created_by", "assigned_cleaner")
    if getattr(request.user, "role", None) == "CLEANER":
        qs = qs.filter(assigned_cleaner=request.user)
    jobs = qs[:200]
    return render(request, "jobs/job_list.html", {"jobs": jobs})


@role_required("MANAGER", "SELLER")
def job_create(request):
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.created_by = request.user
            job.save()
            form.save_m2m()
            return redirect("job_detail", pk=job.pk)
    else:
        form = JobForm()
    return render(request, "jobs/job_form.html", {"form": form})


@login_required
def job_detail(request, pk: int):
    job = get_object_or_404(Job.objects.select_related("customer", "created_by", "assigned_cleaner"), pk=pk)
    return render(request, "jobs/job_detail.html", {"job": job})


@login_required
def add_customer_to_map(request, pk: int):
    job = get_object_or_404(Job, pk=pk)
    customer = job.customer

    # Check if house already exists for this address
    from geolocation.models import House
    if House.objects.filter(address=customer.address).exists():
        messages.warning(request, f"A house with address '{customer.address}' already exists on the map.")
        return redirect("job_detail", pk=pk)

    # Geocode the address
    from geolocation.utils import geocode_address
    full_address = f"{customer.address}, {customer.city}, {customer.state} {customer.zip_code}".strip(", ")
    lat, lng = geocode_address(full_address)

    if lat is None or lng is None:
        messages.error(request, f"Could not geocode address: {full_address}")
        return redirect("job_detail", pk=pk)

    # Create the house
    house = House.objects.create(
        address=customer.address,
        latitude=lat,
        longitude=lng,
        status='NO_ANSWER',  # Default status
        created_by=request.user,
    )
    messages.success(request, f"Added {customer.address} to the map.")
    return redirect("job_detail", pk=pk)
