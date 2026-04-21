from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from accounts.permissions import role_required
from .models import Sale, SalesEntry
from .forms import HouseInteractionCreateForm, SaleForm, SaleJobForm
from jobs.models import Job
from geolocation.models import House
from customers.models import Customer


@login_required
def sales_list(request):
    """Display sales entries (daily summaries)"""
    qs = SalesEntry.objects.select_related("user").order_by("-date")
    if getattr(request.user, "role", None) == "SELLER":
        qs = qs.filter(user=request.user)
    entries = qs[:200]
    return render(request, "sales/sales_list.html", {"entries": entries})


@login_required
def sale_list(request):
    """Display individual sales/interactions"""
    qs = Sale.objects.select_related("user", "house", "customer").order_by("-created_at")
    if getattr(request.user, "role", None) == "SELLER":
        qs = qs.filter(user=request.user)
    
    # Filter by status if provided
    status = request.GET.get("status")
    if status:
        qs = qs.filter(status=status)
    
    sales = qs[:500]
    status_choices = Sale._meta.get_field("status").choices
    return render(
        request,
        "sales/sale_list.html",
        {"sales": sales, "status": status, "status_choices": status_choices},
    )


@login_required
def sale_create(request, house_id: int = None):
    """Create a new sale interaction"""
    house = None
    if house_id:
        house = get_object_or_404(House, pk=house_id)
    
    if request.method == "POST":
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            sale.user = request.user
            sale.save()
            # Keep house marker/status in sync with latest interaction.
            if sale.house_id:
                House.objects.filter(pk=sale.house_id).update(status=sale.status)
            messages.success(request, "Sale recorded successfully!")
            return redirect("sale_list")
    else:
        form = SaleForm(initial={"house": house})
    
    return render(request, "sales/sale_form.html", {"form": form, "house": house})


@login_required
def sale_edit(request, pk: int):
    """Edit an existing house interaction (mainly status/notes/quote)."""
    sale = get_object_or_404(Sale.objects.select_related("house", "customer"), pk=pk)

    if request.method == "POST":
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            sale = form.save()
            if sale.house_id:
                House.objects.filter(pk=sale.house_id).update(status=sale.status)
            messages.success(request, "House interaction updated.")
            return redirect("sale_detail", pk=sale.pk)
    else:
        form = SaleForm(instance=sale)

    return render(request, "sales/sale_form.html", {"form": form, "house": sale.house})

@login_required
def sale_detail(request, pk: int):
    """View sale details"""
    sale = get_object_or_404(Sale.objects.select_related("user", "house", "customer"), pk=pk)
    return render(request, "sales/sale_detail.html", {"sale": sale})


@role_required("MANAGER", "SELLER")
def sale_to_job(request, pk: int):
    """Convert a sale to a job (drag & drop to calendar slot)"""
    sale = get_object_or_404(Sale, pk=pk)
    
    if request.method == "POST":
        form = SaleJobForm(request.POST)
        if form.is_valid():
            customer = form.cleaned_data["customer"]

            job = Job.objects.create(
                customer=customer,
                sale=sale,
                created_by=sale.user,
                job_type=form.cleaned_data.get("job_type"),
                scheduled_date=form.cleaned_data.get("scheduled_date"),
                scheduled_start_time=form.cleaned_data.get("scheduled_start_time"),
                scheduled_end_time=form.cleaned_data.get("scheduled_end_time"),
                assigned_cleaner=form.cleaned_data.get("assigned_cleaner"),
                price=form.cleaned_data.get("price"),
                description=form.cleaned_data.get("description"),
                status="SCHEDULED",
            )
            messages.success(request, f"Job created from sale!")
            return redirect("job_detail", pk=job.pk)
    else:
        initial = {"customer": sale.customer, "price": sale.quote_price}
        # Optional prefill when dropping on calendar
        if request.GET.get("date"):
            initial["scheduled_date"] = request.GET.get("date")
        if request.GET.get("start"):
            initial["scheduled_start_time"] = request.GET.get("start")
        if request.GET.get("end"):
            initial["scheduled_end_time"] = request.GET.get("end")
        form = SaleJobForm(initial=initial)
    
    return render(request, "sales/sale_to_job.html", {"form": form, "sale": sale})


@login_required
def sales_bank(request):
    """Sales bank sidebar - recent sales available for scheduling"""
    # Get recent sales that don't have a job yet
    recent_sales = Sale.objects.filter(
        job__isnull=True,
        status__in=["SOLD", "LEAD", "COME_BACK"]
    ).select_related("user", "customer", "house").order_by("-created_at")[:50]
    
    return render(request, "sales/sales_bank.html", {"sales": recent_sales})


@login_required
def api_sales_bank(request):
    """API endpoint for sales bank data (JSON)"""
    import json
    from django.http import JsonResponse
    
    recent_sales = Sale.objects.filter(
        job__isnull=True,
        status__in=["SOLD", "LEAD", "COME_BACK"]
    ).select_related("user", "customer", "house").order_by("-created_at")[:200]
    
    data = [
        {
            "id": sale.id,
            "customer": str(sale.customer) if sale.customer else "",
            "house_address": getattr(sale.house, "address", ""),
            "status": sale.get_status_display(),
            "status_code": sale.status,
            "open_day": sale.open_day.isoformat() if sale.open_day else None,
            "quote_price": str(sale.quote_price) if getattr(sale, "quote_price", None) is not None else None,
            "created_at": sale.created_at.isoformat(),
            "url": f"/sales/sale/{sale.id}/to-job/",
        }
        for sale in recent_sales
    ]
    
    return JsonResponse({"sales": data})


@login_required
def house_interaction_create(request):
    """
    Create a House, and optionally log an interaction (Sale).
    If interaction_status is left blank, only the house is created.
    """
    initial = {}
    try:
        # Kept for backward compatibility with old links, but we no longer ask for lat/lng in the form.
        if request.GET.get("lat"):
            float(request.GET.get("lat"))
        if request.GET.get("lng"):
            float(request.GET.get("lng"))
    except ValueError:
        pass
    if request.GET.get("address"):
        initial["address"] = request.GET.get("address")

    if request.method == "POST":
        form = HouseInteractionCreateForm(request.POST)
        if form.is_valid():
            house = form.create_house(user=request.user)

            status = form.cleaned_data.get("interaction_status") or ""
            if status:
                House.objects.filter(pk=house.pk).update(status=status)

                customer = None
                if status == "SOLD":
                    customer = Customer.objects.create(
                        first_name=form.cleaned_data.get("customer_first_name", "").strip(),
                        last_name=form.cleaned_data.get("customer_last_name", "").strip(),
                        phone=form.cleaned_data.get("customer_phone", "").strip(),
                        address=house.address,
                    )

                open_day = form.cleaned_data.get("open_day")
                tentative_date = form.cleaned_data.get("tentative_date")
                if not open_day and tentative_date:
                    open_day = timezone.make_aware(
                        timezone.datetime.combine(tentative_date, timezone.datetime.min.time())
                    )

                sale = Sale.objects.create(
                    user=request.user,
                    house=house,
                    customer=customer,
                    status=status,
                    quote_price=form.cleaned_data.get("quote_price"),
                    open_day=open_day,
                    notes=form.cleaned_data.get("notes", ""),
                )
                messages.success(request, "Interaction recorded.")
                return redirect("sale_detail", pk=sale.pk)

            messages.success(request, "House created.")
            return redirect("map")
    else:
        form = HouseInteractionCreateForm(initial=initial)

    return render(request, "sales/house_interaction_form.html", {"form": form})
