from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accounts.permissions import role_required

from .models import Invoice


@login_required
def invoice_list(request):
    qs = Invoice.objects.select_related("customer", "job").order_by("-created_at")
    invoices = qs[:200]
    return render(request, "invoices/invoice_list.html", {"invoices": invoices})
