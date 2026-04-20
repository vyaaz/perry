from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.utils import timezone

from accounts.permissions import role_required

from .forms import JobAssignCleanerForm, JobForm, JobImportForm
from .models import Job, JobCleaner
from .utils import parse_job_csv


@login_required
def job_list(request):
    qs = Job.objects.select_related("customer", "created_by", "assigned_cleaner")
    if getattr(request.user, "role", None) == "CLEANER":
        qs = qs.filter(assigned_cleaner=request.user)
    jobs = qs[:200]
    return render(request, "jobs/job_list.html", {"jobs": jobs})


@role_required("MANAGER", "SELLER")
def job_import(request):
    if request.method == "POST":
        form = JobImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data["csv_file"]
            result = parse_job_csv(csv_file, created_by=request.user)
            messages.success(
                request,
                f"Imported {result['processed']} rows: {result['created']} created, {result['updated']} updated.",
            )
            for error in result["errors"]:
                messages.warning(request, error)
            return redirect("job_list")
    else:
        form = JobImportForm()
    return render(request, "jobs/job_import.html", {"form": form})


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
    assigned_cleaners = job.cleaners.select_related("cleaner").all()
    return render(request, "jobs/job_detail.html", {"job": job, "assigned_cleaners": assigned_cleaners})


@login_required
def job_assign_cleaner(request, pk: int):
    job = get_object_or_404(Job.objects.select_related("customer"), pk=pk)

    # Cleaners can only assign themselves; managers can assign anyone.
    if getattr(request.user, "role", None) not in {"MANAGER", "CLEANER"}:
        messages.error(request, "You don't have permission to assign cleaners.")
        return redirect("job_detail", pk=pk)

    if request.method == "POST":
        form = JobAssignCleanerForm(request.POST, request_user=request.user)
        if form.is_valid():
            cleaner = form.cleaned_data["cleaner"]
            JobCleaner.objects.get_or_create(job=job, cleaner=cleaner)
            # Keep single assigned_cleaner in sync with last assignment.
            job.assigned_cleaner = cleaner
            job.save(update_fields=["assigned_cleaner"])
            messages.success(request, "Cleaner assigned.")
            return redirect("job_detail", pk=pk)
    else:
        form = JobAssignCleanerForm(request_user=request.user)

    return render(request, "jobs/job_assign_cleaner.html", {"job": job, "form": form})


@login_required
def job_mark_complete(request, pk: int):
    job = get_object_or_404(Job, pk=pk)
    role = getattr(request.user, "role", None)
    if role != "MANAGER" and job.assigned_cleaner_id != request.user.id:
        messages.error(request, "Only the assigned cleaner or a manager can complete this job.")
        return redirect("job_detail", pk=pk)

    job.status = "COMPLETED"
    job.completion_date = timezone.localdate()
    job.save(update_fields=["status", "completion_date"])
    messages.success(request, "Job marked completed.")
    return redirect("job_detail", pk=pk)


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
