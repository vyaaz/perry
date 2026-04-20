from django.conf import settings
from django.db import models


class SaleStatus(models.TextChoices):
    SOLD = "SOLD", "Sold"
    NO_ANSWER = "NO_ANSWER", "No Answer"
    REJECTED = "REJECTED", "Rejected"
    NON_DM = "NON_DM", "Non DM"
    COME_BACK = "COME_BACK", "Come Back"
    LEAD = "LEAD", "Lead"


class Sale(models.Model):
    """
    Represents a single sale interaction with a house/customer.
    Created when an employee interacts with a house and logs the outcome.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="sales")
    house = models.ForeignKey("geolocation.House", on_delete=models.CASCADE, related_name="sales")
    customer = models.ForeignKey("customers.Customer", on_delete=models.CASCADE, related_name="sales", null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=SaleStatus.choices, default=SaleStatus.NO_ANSWER)
    
    # Optional open day/time slot
    open_day = models.DateTimeField(null=True, blank=True, help_text="Scheduled open day if customer agreed")
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Sales"

    def __str__(self) -> str:
        return f"{self.user} · {self.house.address} · {self.get_status_display()}"


class SalesEntry(models.Model):
    """
    Daily sales summary for tracking purposes.
    Aggregates sales data per user per day.
    """
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
