from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import role_required

from .forms import InvoiceForm
from .models import Invoice


@login_required
def invoice_list(request):
    qs = Invoice.objects.select_related("customer", "job").order_by("-created_at")
    invoices = qs[:200]
    return render(request, "invoices/invoice_list.html", {"invoices": invoices})


@role_required("MANAGER", "SELLER")
def invoice_create(request):
    initial = {}
    job_pk = request.GET.get('job')
    if job_pk:
        try:
            from jobs.models import Job
            job = Job.objects.get(pk=job_pk)
            initial = {'customer': job.customer, 'job': job}
        except Job.DoesNotExist:
            pass

    if request.method == "POST":
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save()
            return redirect("invoice_list")
    else:
        form = InvoiceForm(initial=initial)
    return render(request, "invoices/invoice_form.html", {"form": form})
