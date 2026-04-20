from django import forms
from django.contrib.auth import get_user_model

from .models import Sale
from customers.models import Customer
from jobs.models import JobType
from geolocation.models import House, HouseStatus

User = get_user_model()


class SaleForm(forms.ModelForm):
    """Form to create or update a sale interaction with a house"""
    
    # Customer info fields - either select existing customer or create new inline
    first_name = forms.CharField(max_length=80, required=False, label="Customer First Name")
    last_name = forms.CharField(max_length=80, required=False, label="Customer Last Name")
    phone = forms.CharField(max_length=30, required=False, label="Customer Phone")
    email = forms.EmailField(required=False, label="Customer Email")
    address = forms.CharField(max_length=255, required=False, label="Customer Address")
    city = forms.CharField(max_length=120, required=False, label="Customer City")
    state = forms.CharField(max_length=60, required=False, label="Customer State")
    zip_code = forms.CharField(max_length=20, required=False, label="Customer Zip Code")
    
    class Meta:
        model = Sale
        fields = [
            "house",
            "customer",
            "status",
            "open_day",
            "notes",
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing + " form-control").strip()
        
        # If editing existing sale, populate customer fields
        if self.instance.pk and self.instance.customer:
            self.fields["first_name"].initial = self.instance.customer.first_name
            self.fields["last_name"].initial = self.instance.customer.last_name
            self.fields["phone"].initial = self.instance.customer.phone
            self.fields["email"].initial = self.instance.customer.email
            self.fields["address"].initial = self.instance.customer.address
            self.fields["city"].initial = self.instance.customer.city
            self.fields["state"].initial = self.instance.customer.state
            self.fields["zip_code"].initial = self.instance.customer.zip_code
    
    def save(self, commit=True):
        sale = super().save(commit=False)
        
        # Create or update customer if customer fields are provided
        if any([
            self.cleaned_data.get("first_name"),
            self.cleaned_data.get("last_name"),
            self.cleaned_data.get("phone"),
            self.cleaned_data.get("email"),
        ]):
            customer, created = Customer.objects.get_or_create(
                first_name=self.cleaned_data.get("first_name", ""),
                last_name=self.cleaned_data.get("last_name", ""),
                defaults={
                    "phone": self.cleaned_data.get("phone", ""),
                    "email": self.cleaned_data.get("email", ""),
                    "address": self.cleaned_data.get("address", ""),
                    "city": self.cleaned_data.get("city", ""),
                    "state": self.cleaned_data.get("state", ""),
                    "zip_code": self.cleaned_data.get("zip_code", ""),
                }
            )
            
            # Update customer fields if updating existing customer
            if not created:
                customer.phone = self.cleaned_data.get("phone", "") or customer.phone
                customer.email = self.cleaned_data.get("email", "") or customer.email
                customer.address = self.cleaned_data.get("address", "") or customer.address
                customer.city = self.cleaned_data.get("city", "") or customer.city
                customer.state = self.cleaned_data.get("state", "") or customer.state
                customer.zip_code = self.cleaned_data.get("zip_code", "") or customer.zip_code
                customer.save()
            
            sale.customer = customer
        
        if commit:
            sale.save()
        
        return sale


class SaleJobForm(forms.Form):
    """Form to convert a sale to a job with scheduling"""
    
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all().order_by("last_name", "first_name"),
        required=False,
        label="Customer",
        help_text="Required to create a job. Select an existing customer or enter a new one below.",
    )
    customer_first_name = forms.CharField(max_length=80, required=False, label="New customer first name")
    customer_last_name = forms.CharField(max_length=80, required=False, label="New customer last name")
    customer_phone = forms.CharField(max_length=30, required=False, label="New customer phone")

    job_type = forms.ChoiceField(
        choices=JobType.choices,
        required=True,
    )
    scheduled_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    scheduled_start_time = forms.TimeField(widget=forms.TimeInput(attrs={"type": "time"}))
    scheduled_end_time = forms.TimeField(widget=forms.TimeInput(attrs={"type": "time"}))
    assigned_cleaner = forms.ModelChoiceField(
        queryset=User.objects.filter(role="CLEANER"),
        required=False,
        label="Assign Cleaner",
    )
    price = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
    description = forms.CharField(widget=forms.Textarea, required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing + " form-control").strip()

    def clean(self):
        cleaned = super().clean()
        customer = cleaned.get("customer")
        has_new_name = cleaned.get("customer_first_name") and cleaned.get("customer_last_name")
        has_new_phone = bool(cleaned.get("customer_phone"))
        if not customer and not (has_new_name and has_new_phone):
            raise forms.ValidationError(
                "Select a customer or enter new customer first/last name and phone."
            )
        return cleaned


class HouseInteractionCreateForm(forms.Form):
    address = forms.CharField(max_length=255, widget=forms.TextInput(attrs={"class": "form-control"}))
    latitude = forms.DecimalField(max_digits=9, decimal_places=6, widget=forms.NumberInput(attrs={"class": "form-control", "step": "any"}))
    longitude = forms.DecimalField(max_digits=9, decimal_places=6, widget=forms.NumberInput(attrs={"class": "form-control", "step": "any"}))

    # Optional: if set, we will create a Sale interaction too
    interaction_status = forms.ChoiceField(
        required=False,
        choices=[("", "— Create house only —")] + list(Sale._meta.get_field("status").choices),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Interaction outcome",
    )
    open_day = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
        help_text="Optional appointment time if agreed.",
    )
    customer_first_name = forms.CharField(
        max_length=80,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Customer first name",
    )
    customer_last_name = forms.CharField(
        max_length=80,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Customer last name",
    )
    customer_phone = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Customer phone",
    )
    tentative_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        label="Tentative date",
        help_text="If you don’t have a time yet, pick a date and we’ll set it as tentative.",
    )
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}))

    def clean(self):
        cleaned = super().clean()
        status = (cleaned.get("interaction_status") or "").strip()
        is_sale = status == "SOLD"
        if is_sale:
            if not (cleaned.get("customer_first_name") and cleaned.get("customer_last_name")):
                raise forms.ValidationError("Customer first + last name are required for SOLD.")
            if not cleaned.get("customer_phone"):
                raise forms.ValidationError("Customer phone number is required for SOLD.")
            if not (cleaned.get("open_day") or cleaned.get("tentative_date")):
                raise forms.ValidationError("Provide either a tentative date or an open day/time for SOLD.")
        return cleaned

    def create_house(self, *, user):
        house = House.objects.create(
            address=self.cleaned_data["address"],
            latitude=self.cleaned_data["latitude"],
            longitude=self.cleaned_data["longitude"],
            status=HouseStatus.NO_ANSWER,
            created_by=user,
        )
        return house
