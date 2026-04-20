import json
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from jobs.models import Job
from .models import CalendarBlock


@login_required
def schedule_list(request):
    return render(request, "scheduling/schedule_list.html")


@login_required
@require_GET
def api_jobs(request):
    """
    FullCalendar events feed for scheduled jobs.
    """
    qs = Job.objects.select_related("customer").filter(
        scheduled_date__isnull=False,
        scheduled_start_time__isnull=False,
        scheduled_end_time__isnull=False,
    )[:1000]

    events = []
    for j in qs:
        start = timezone.make_aware(
            timezone.datetime.combine(j.scheduled_date, j.scheduled_start_time)
        )
        end = timezone.make_aware(
            timezone.datetime.combine(j.scheduled_date, j.scheduled_end_time)
        )
        events.append(
            {
                "id": str(j.pk),
                "title": f"{j.customer} · #{j.pk}",
                "start": start.isoformat(),
                "end": end.isoformat(),
                "url": f"/jobs/{j.pk}/",
            }
        )
    return JsonResponse(events, safe=False)


@login_required
@require_POST
def api_job_move(request, pk: int):
    """
    Update job scheduled time when dragged on calendar.
    """
    job = get_object_or_404(Job, pk=pk)
    try:
        payload = json.loads(request.body.decode("utf-8"))
        start = timezone.datetime.fromisoformat(payload["start"])
        end = timezone.datetime.fromisoformat(payload["end"])
        if timezone.is_naive(start):
            start = timezone.make_aware(start)
        if timezone.is_naive(end):
            end = timezone.make_aware(end)
    except Exception:
        return JsonResponse({"ok": False, "error": "Invalid payload"}, status=400)

    job.scheduled_date = start.date()
    job.scheduled_start_time = start.time().replace(microsecond=0)
    job.scheduled_end_time = end.time().replace(microsecond=0)
    job.status = "SCHEDULED"
    job.save(update_fields=["scheduled_date", "scheduled_start_time", "scheduled_end_time", "status"])

    # Keep calendar blocks loosely in sync if they exist
    if job.assigned_cleaner_id:
        CalendarBlock.objects.update_or_create(
            job=job,
            assigned_user_id=job.assigned_cleaner_id,
            defaults={"start_time": start, "end_time": end},
        )

    return JsonResponse({"ok": True})
