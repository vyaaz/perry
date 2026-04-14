from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class UserRole(models.TextChoices):
    MANAGER = "MANAGER", "Manager"
    SELLER = "SELLER", "Seller"
    CLEANER = "CLEANER", "Cleaner"


class CommissionTier(models.TextChoices):
    AMATEUR = "AMATEUR", "Amateur"
    INTERMEDIATE = "INTERMEDIATE", "Intermediate"
    ELITE = "ELITE", "Elite"


class User(AbstractUser):
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=30, blank=True)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.SELLER)

    commission_tier = models.CharField(
        max_length=20, choices=CommissionTier.choices, default=CommissionTier.AMATEUR
    )
    hire_date = models.DateField(null=True, blank=True, default=timezone.now)

    def get_full_name(self) -> str:  # type: ignore[override]
        full = f"{self.first_name} {self.last_name}".strip()
        return full or self.username

    def total_sales(self):
        """
        Total invoiced revenue for jobs created by this user.
        Kept simple: uses Invoice.amount, regardless of paid status.
        """
        return (
            self.created_jobs.select_related("invoice")
            .aggregate(total=Sum("invoice__amount"))
            .get("total")
            or 0
        )

    def total_jobs_completed(self):
        return self.assigned_jobs.filter(status="COMPLETED").count()
