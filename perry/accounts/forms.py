from django import forms
from django.contrib.auth import get_user_model

from .models import UserRole

User = get_user_model()


class UserRegistrationForm(forms.ModelForm):
    """Form for user registration with employee/manager selection"""
    
    ACCOUNT_TYPE_CHOICES = [
        ("EMPLOYEE", "Employee"),
        ("MANAGER", "Manager"),
    ]

    account_type = forms.ChoiceField(
        choices=ACCOUNT_TYPE_CHOICES,
        label="Account Type",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    password_confirm = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "phone_number", "commission_tier"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "commission_tier": forms.Select(attrs={"class": "form-control"}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        account_type = self.cleaned_data.get("account_type")
        if account_type == "MANAGER":
            user.role = UserRole.MANAGER
        else:
            user.role = UserRole.SELLER
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""

    is_seller = forms.BooleanField(required=False, label="Seller")
    is_cleaner = forms.BooleanField(required=False, label="Cleaner")
    
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone_number", "commission_tier", "profile_image"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "commission_tier": forms.Select(attrs={"class": "form-control"}),
            "profile_image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        role = getattr(self.instance, "role", "") if self.instance else ""
        self.fields["is_seller"].initial = role in {"SELLER", "BOTH"}
        self.fields["is_cleaner"].initial = role in {"CLEANER", "BOTH"}

        # Ensure Bootstrap on non-widget-decorated fields
        for name, field in self.fields.items():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing + " form-control").strip()

    def clean(self):
        cleaned = super().clean()
        is_seller = bool(cleaned.get("is_seller"))
        is_cleaner = bool(cleaned.get("is_cleaner"))

        if is_seller and is_cleaner:
            cleaned["role"] = UserRole.BOTH
        elif is_seller:
            cleaned["role"] = UserRole.SELLER
        elif is_cleaner:
            cleaned["role"] = UserRole.CLEANER
        else:
            raise forms.ValidationError("Pick at least one: Seller and/or Cleaner.")

        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data["role"]
        if commit:
            user.save()
        return user


class EmployeeCommissionForm(forms.ModelForm):
    """
    Manager-only form to set commission for an employee:
    - Either pick a tier (AMATEUR/INTERMEDIATE/ELITE)
    - Or override with an exact percentage
    """

    class Meta:
        model = User
        fields = ["role", "commission_tier", "commission_override_percentage"]
        widgets = {
            "role": forms.Select(attrs={"class": "form-control"}),
            "commission_tier": forms.Select(attrs={"class": "form-control"}),
            "commission_override_percentage": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0", "max": "100"}
            ),
        }

    def clean_commission_override_percentage(self):
        value = self.cleaned_data.get("commission_override_percentage")
        if value is None:
            return value
        if value < 0 or value > 100:
            raise forms.ValidationError("Commission must be between 0 and 100.")
        return value
