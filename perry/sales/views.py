from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import SalesEntry


@login_required
def sales_list(request):
    qs = SalesEntry.objects.select_related("user").order_by("-date")
    if getattr(request.user, "role", None) == "SELLER":
        qs = qs.filter(user=request.user)
    entries = qs[:200]
    return render(request, "sales/sales_list.html", {"entries": entries})
