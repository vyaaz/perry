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
    
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone_number", "commission_tier"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "commission_tier": forms.Select(attrs={"class": "form-control"}),
        }
