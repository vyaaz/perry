from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.shortcuts import render

from invoices.models import Invoice
from jobs.models import Job
from sales.models import Sale
from accounts.models import User


@login_required
def dashboard(request):
    today = timezone.localdate()
    start_of_month = today.replace(day=1)
    
    user = request.user
    is_manager = user.role == "MANAGER"
    is_seller = user.role == "SELLER"
    is_cleaner = user.role == "CLEANER"
    is_both = user.role == "BOTH"

    # Filter context based on user role
    if is_manager:
        # Manager dashboard - shows company-wide statistics
        jobs_today = Job.objects.filter(scheduled_date=today).select_related("customer", "assigned_cleaner")
        unpaid_invoices = Invoice.objects.filter(paid=False).select_related("customer", "job")[:10]
        
        revenue_sold_this_month = (
            Invoice.objects.filter(created_at__date__gte=start_of_month)
            .aggregate(total=Sum("amount"))
            .get("total") or 0
        )
        revenue_paid_this_month = (
            Invoice.objects.filter(created_at__date__gte=start_of_month, paid=True)
            .aggregate(total=Sum("amount"))
            .get("total") or 0
        )
        
        # Top performers
        top_sellers = (
            User.objects.filter(role__in=["SELLER", "BOTH"])
            .annotate(total_sales=Sum("created_jobs__invoice__amount"))
            .order_by("-total_sales")[:5]
        )
        
        top_cleaners = (
            User.objects.filter(role__in=["CLEANER", "BOTH"])
            .annotate(jobs_completed=Count("assigned_jobs", filter=Q(assigned_jobs__status="COMPLETED")))
            .order_by("-jobs_completed")[:5]
        )
        
        context = {
            "is_manager": True,
            "jobs_today": jobs_today,
            "unpaid_invoices": unpaid_invoices,
            "revenue_sold_this_month": revenue_sold_this_month,
            "revenue_paid_this_month": revenue_paid_this_month,
            "top_sellers": top_sellers,
            "top_cleaners": top_cleaners,
        }
        
    elif is_seller or is_both:
        # Seller dashboard - individual statistics
        my_sales = Sale.objects.filter(user=user)
        my_jobs = Job.objects.filter(created_by=user)
        
        total_interactions = my_sales.count()
        successful_sales = my_sales.filter(status="SOLD").count()
        closing_ratio = (successful_sales / total_interactions * 100) if total_interactions > 0 else 0
        
        my_revenue = (
            Invoice.objects.filter(job__created_by=user, job__invoice__isnull=False)
            .aggregate(total=Sum("amount"))
            .get("total") or 0
        )
        
        my_commission = user.individual_revenue()
        
        upcoming_jobs = my_jobs.filter(scheduled_date__gte=today).order_by("scheduled_date")[:10]
        recent_sales = my_sales.order_by("-created_at")[:10]
        
        context = {
            "is_seller": True,
            "total_interactions": total_interactions,
            "successful_sales": successful_sales,
            "closing_ratio": closing_ratio,
            "my_revenue": my_revenue,
            "my_commission": my_commission,
            "upcoming_jobs": upcoming_jobs,
            "recent_sales": recent_sales,
        }
        
    elif is_cleaner:
        # Cleaner dashboard - job assignments and completion
        assigned_jobs = Job.objects.filter(cleaners__cleaner=user).select_related("customer")
        completed_jobs = assigned_jobs.filter(status="COMPLETED")
        upcoming_jobs = assigned_jobs.filter(scheduled_date__gte=today).order_by("scheduled_date")[:10]
        
        jobs_completed_this_month = completed_jobs.filter(completion_date__gte=start_of_month).count()
        my_commission = user.individual_revenue()
        
        context = {
            "is_cleaner": True,
            "assigned_jobs": assigned_jobs,
            "completed_jobs": completed_jobs.count(),
            "upcoming_jobs": upcoming_jobs,
            "jobs_completed_this_month": jobs_completed_this_month,
            "my_commission": my_commission,
        }
    else:
        context = {"error": "Unknown user role"}

    return render(request, "dashboard/dashboard.html", context)
