from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum, Q
from django.utils import timezone


class UserRole(models.TextChoices):
    MANAGER = "MANAGER", "Manager"
    SELLER = "SELLER", "Seller"
    CLEANER = "CLEANER", "Cleaner"
    BOTH = "BOTH", "Seller + Cleaner"


class CommissionTier(models.TextChoices):
    AMATEUR = "AMATEUR", "Amateur"
    INTERMEDIATE = "INTERMEDIATE", "Intermediate"
    ELITE = "ELITE", "Elite"


class User(AbstractUser):
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=30, blank=True)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.SELLER)
    profile_image = models.ImageField(upload_to="profile_pics/", null=True, blank=True)

    commission_tier = models.CharField(
        max_length=20, choices=CommissionTier.choices, default=CommissionTier.AMATEUR
    )
    commission_override_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="If set, overrides the tier percentage (e.g. 12.5 for 12.5%).",
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

    def closing_ratio(self):
        """
        Calculate closing ratio for sellers based on house interactions (sales).
        Ratio = number of successful sales / total house interactions
        """
        from sales.models import Sale
        total_interactions = Sale.objects.filter(user=self).count()
        successful_sales = Sale.objects.filter(user=self, status="SOLD").count()
        return (successful_sales / total_interactions) if total_interactions > 0 else 0.0

    def individual_revenue(self):
        """
        Total revenue this employee has earned through commission.
        Includes both seller and cleaner roles.
        """
        return (
            self.payments.aggregate(total=Sum("amount")).get("total") or 0
        )


class CommissionBracket(models.Model):
    """
    Commission brackets for employees on a per-sale or per-job basis.
    Managers can assign different commission rates based on various criteria.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commission_brackets")
    job = models.ForeignKey("jobs.Job", on_delete=models.CASCADE, related_name="commission_brackets", null=True, blank=True)
    sale = models.ForeignKey("sales.Sale", on_delete=models.CASCADE, related_name="commission_brackets", null=True, blank=True)
    
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Commission as percentage")
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Fixed commission amount")
    
    role = models.CharField(max_length=20, choices=[("SELLER", "Seller"), ("CLEANER", "Cleaner")])
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        target = self.job or self.sale
        return f"{self.user} · {self.role} · {self.commission_percentage}% · {target}"
