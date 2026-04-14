from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import CalendarBlock


@login_required
def schedule_list(request):
    blocks = CalendarBlock.objects.select_related("job", "job__customer", "assigned_user").order_by("start_time")[:200]
    return render(request, "scheduling/schedule_list.html", {"blocks": blocks})
