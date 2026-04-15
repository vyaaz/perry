from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from django.shortcuts import render

from invoices.models import Invoice
from jobs.models import Job


@login_required
def dashboard(request):
    today = timezone.localdate()
    start_of_month = today.replace(day=1)

    jobs_today = Job.objects.filter(scheduled_date=today).select_related("customer", "assigned_cleaner")
    unpaid_invoices = Invoice.objects.filter(paid=False).select_related("customer", "job")[:10]
    revenue_sold_this_month = (
        Invoice.objects.filter(created_at__date__gte=start_of_month).aggregate(total=Sum("amount")).get("total")
        or 0
    )
    revenue_paid_this_month = (
        Invoice.objects.filter(created_at__date__gte=start_of_month, paid=True).aggregate(total=Sum("amount")).get("total")
        or 0
    )

    top_seller = None
    top_cleaner = None

    context = {
        "jobs_today": jobs_today,
        "unpaid_invoices": unpaid_invoices,
        "revenue_sold_this_month": revenue_sold_this_month,
        "revenue_paid_this_month": revenue_paid_this_month,
        "top_seller": top_seller,
        "top_cleaner": top_cleaner,
    }
    return render(request, "dashboard/dashboard.html", context)
