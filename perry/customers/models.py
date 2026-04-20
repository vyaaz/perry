from django.db import models
from datetime import timedelta, date


class Customer(models.Model):
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)

    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120, blank=True)
    state = models.CharField(max_length=60, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)

    notes = models.TextField(blank=True)
    
    # Track when the customer first became a client (for bi-yearly follow-up)
    first_job_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def get_next_scheduled_jobs(self):
        """
        Get the next two jobs scheduled bi-yearly from the customer's first job.
        Returns a list of scheduled dates.
        """
        if not self.first_job_date:
            return []
        
        job_dates = []
        current_date = self.first_job_date
        
        # Schedule two more jobs: 6 months and 12 months from first job
        for months_offset in [6, 12]:
            scheduled_date = current_date + timedelta(days=30 * months_offset)  # Approximate
            job_dates.append(scheduled_date)
        
        return job_dates
