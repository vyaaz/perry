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
        self.fields["job"].queryset = self.fields["job"].queryset.filter(invoice__isnull=True)