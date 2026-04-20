from django import forms

from .models import Invoice


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ["customer", "job", "amount", "completion_date", "paid"]
        widgets = {
            "completion_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show jobs that don't have invoices yet
        jobs = self.fields["job"].queryset.filter(invoice__isnull=True)
        choices = [('', '---------')]
        for job in jobs:
            choices.append((job.pk, f"{job} - ${job.price}"))
        self.fields["job"].choices = choices