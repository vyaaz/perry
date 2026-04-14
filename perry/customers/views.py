from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import role_required
from invoices.models import Invoice
from jobs.models import Job

from .forms import CustomerForm
from .models import Customer


@login_required
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, "customers/customer_list.html", {"customers": customers})


@role_required("MANAGER", "SELLER")
def customer_create(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            return redirect("customer_detail", pk=customer.pk)
    else:
        form = CustomerForm()
    return render(request, "customers/customer_form.html", {"form": form})


@login_required
def customer_detail(request, pk: int):
    customer = get_object_or_404(Customer, pk=pk)
    jobs = Job.objects.filter(customer=customer).select_related("assigned_cleaner", "created_by")
    invoices = Invoice.objects.filter(customer=customer).select_related("job")
    return render(
        request,
        "customers/customer_detail.html",
        {"customer": customer, "jobs": jobs, "invoices": invoices},
    )
