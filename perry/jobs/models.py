from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class JobType(models.TextChoices):
    WINDOW_WASH = "WINDOW_WASH", "Window Wash"
    PRESSURE_WASH = "PRESSURE_WASH", "Pressure Wash"
    GUTTER_CLEAN = "GUTTER_CLEAN", "Gutter Clean"
    OTHER = "OTHER", "Other"


class JobStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SCHEDULED = "SCHEDULED", "Scheduled"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"


class Job(models.Model):
    customer = models.ForeignKey("customers.Customer", on_delete=models.CASCADE, related_name="jobs")
    sale = models.OneToOneField("sales.Sale", on_delete=models.SET_NULL, null=True, blank=True, related_name="job")
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_jobs"
    )
    assigned_cleaner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="assigned_jobs",
        limit_choices_to={"role": "CLEANER"},
    )

    job_type = models.CharField(max_length=30, choices=JobType.choices, default=JobType.WINDOW_WASH)
    description = models.TextField(blank=True)
    estimated_time = models.PositiveIntegerField(help_text="Minutes", default=120)  # 2 hours default
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    status = models.CharField(max_length=20, choices=JobStatus.choices, default=JobStatus.PENDING)
    scheduled_date = models.DateField(null=True, blank=True)
    scheduled_start_time = models.TimeField(null=True, blank=True)
    scheduled_end_time = models.TimeField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.customer} · {self.get_job_type_display()} · {self.get_status_display()}"

    @property
    def salesman(self):
        """Auto-assigned salesman from the sale if available"""
        if self.sale:
            return self.sale.user
        return self.created_by
    
    def get_assigned_cleaners(self):
        """Get all cleaners assigned to this job"""
        return self.cleaners.all()


class JobCleaner(models.Model):
    """
    Junction table to support multiple cleaners assigned to a single job.
    """
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="cleaners")
    cleaner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="jobs_as_cleaner",
        limit_choices_to={"role": "CLEANER"},
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("job", "cleaner")]

    def __str__(self) -> str:
        return f"{self.job} · {self.cleaner}"


# Signal to auto-create invoice when job is created
@receiver(post_save, sender=Job)
def create_invoice_for_job(sender, instance, created, **kwargs):
    if created:
        from invoices.models import Invoice
        Invoice.objects.get_or_create(
            job=instance,
            defaults={
                "customer": instance.customer,
                "amount": instance.price,
            }
        )
