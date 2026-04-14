from django import forms

from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            "first_name",
            "last_name",
            "phone",
            "email",
            "address",
            "city",
            "state",
            "zip_code",
            "notes",
        ]

        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                existing = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = (existing + " form-control").strip()

