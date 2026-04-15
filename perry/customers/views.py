from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

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
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect("customer_detail", pk=customer.pk)
    else:
        form = CustomerForm()
    return render(request, "customers/customer_form.html", {"form": form, "next": request.GET.get('next')})


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


@login_required
def add_customer_to_map(request, pk: int):
    customer = get_object_or_404(Customer, pk=pk)

    # Check if house already exists for this address
    from geolocation.models import House
    if House.objects.filter(address=customer.address).exists():
        messages.warning(request, f"A house with address '{customer.address}' already exists on the map.")
        return redirect("customer_detail", pk=pk)

    # Geocode the address
    from geolocation.utils import geocode_address
    full_address = f"{customer.address}, {customer.city}, {customer.state} {customer.zip_code}".strip(", ")
    lat, lng = geocode_address(full_address)

    if lat is None or lng is None:
        messages.error(request, f"Could not geocode address: {full_address}")
        return redirect("customer_detail", pk=pk)

    # Create the house
    house = House.objects.create(
        address=customer.address,
        latitude=lat,
        longitude=lng,
        status='NO_ANSWER',  # Default status
        created_by=request.user,
    )
    messages.success(request, f"Added {customer.address} to the map.")
    return redirect("customer_detail", pk=pk)
