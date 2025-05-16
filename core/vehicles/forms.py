from django import forms
from .models import Vehicle, VehicleBrand, VehicleModel


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ["brand", "model", "license_plate", "vin"]
        widgets = {
            "brand": forms.Select(
                attrs={
                    "class": "form-control form-control-lg",
                }
            ),
            "model": forms.Select(
                attrs={
                    "class": "form-control form-control-lg",
                }
            ),
            "license_plate": forms.TextInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "Placa",
                }
            ),
            "vin": forms.TextInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "VIN",
                }
            ),
        }


class VehicleBrandForm(forms.ModelForm):
    class Meta:
        model = VehicleBrand
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "Marca",
                }
            ),
        }


class VehicleModelForm(forms.ModelForm):
    class Meta:
        model = VehicleModel
        fields = ["brand", "name"]
        widgets = {
            "brand": forms.Select(
                attrs={
                    "class": "form-control form-control-lg",
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "Modelo",
                }
            ),
        }
