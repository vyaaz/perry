from django.conf import settings
from django.db import models


class HouseStatus(models.TextChoices):
    SOLD = "SOLD", "Sold"
    NO_ANSWER = "NO_ANSWER", "No Answer"
    REJECTED = "REJECTED", "Rejected"
    NON_DM = "NON_DM", "Non DM"
    COME_BACK = "COME_BACK", "Come Back"
    LEAD = "LEAD", "Lead"


class House(models.Model):
    address = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    status = models.CharField(max_length=20, choices=HouseStatus.choices, default=HouseStatus.NO_ANSWER)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="houses"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.address} ({self.get_status_display()})"
