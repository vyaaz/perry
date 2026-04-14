from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

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
