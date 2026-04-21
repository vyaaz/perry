from django import forms

from .models import House


class HouseCreateForm(forms.ModelForm):
    class Meta:
        model = House
        fields = ["address", "latitude", "longitude", "status"]
        widgets = {
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "latitude": forms.NumberInput(attrs={"class": "form-control", "step": "any"}),
            "longitude": forms.NumberInput(attrs={"class": "form-control", "step": "any"}),
            "status": forms.Select(attrs={"class": "form-control"}),
        }


class HouseUpdateForm(forms.ModelForm):
    class Meta:
        model = House
        fields = ["address", "status"]
        widgets = {
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
        }

