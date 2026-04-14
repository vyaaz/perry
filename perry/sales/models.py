from django.conf import settings
from django.db import models


class SalesEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="sales_entries")
    date = models.DateField()

    doors_knocked = models.PositiveIntegerField(default=0)
    houses_sold = models.PositiveIntegerField(default=0)
    no_answer = models.PositiveIntegerField(default=0)
    rejected = models.PositiveIntegerField(default=0)
    non_dm = models.PositiveIntegerField(default=0)
    come_back = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-date"]
        unique_together = [("user", "date")]

    def __str__(self) -> str:
        return f"{self.user} · {self.date}"

    @property
    def closing_ratio(self) -> float:
        return (self.houses_sold / self.doors_knocked) if self.doors_knocked else 0.0
