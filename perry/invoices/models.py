from django.conf import settings
from django.db import models


class Invoice(models.Model):
    customer = models.ForeignKey("customers.Customer", on_delete=models.PROTECT, related_name="invoices")
    job = models.OneToOneField("jobs.Job", on_delete=models.PROTECT, related_name="invoice")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    completion_date = models.DateField(null=True, blank=True)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Invoice #{self.pk} · {self.customer} · ${self.amount}"


class PaymentRole(models.TextChoices):
    SELLER = "SELLER", "Seller"
    CLEANER = "CLEANER", "Cleaner"


class WorkerPayment(models.Model):
    invoice = models.ForeignKey("invoices.Invoice", on_delete=models.CASCADE, related_name="payments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    role = models.CharField(max_length=20, choices=PaymentRole.choices)

    class Meta:
        ordering = ["invoice_id", "role"]

    def __str__(self) -> str:
        return f"{self.invoice} · {self.user} · {self.role} · ${self.amount}"
