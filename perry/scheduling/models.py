from django.conf import settings
from django.db import models


class CalendarBlock(models.Model):
    job = models.ForeignKey("jobs.Job", on_delete=models.CASCADE, related_name="calendar_blocks")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    assigned_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="calendar_blocks"
    )

    class Meta:
        ordering = ["start_time"]

    def __str__(self) -> str:
        return f"{self.job} ({self.start_time} - {self.end_time})"
