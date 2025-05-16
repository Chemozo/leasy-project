from django import forms
from .models import Client


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["first_name", "last_name", "document_number"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "Nombre",
                    "autofocus": True,
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "Apellido",
                }
            ),
            "document_number": forms.TextInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "Número de documento",
                }
            ),
        }

    def clean_document_number(self):
        document_number = self.cleaned_data["document_number"]
        if Client.objects.filter(document_number=document_number).exists():
            raise forms.ValidationError("El número de documento ya existe")
        return document_number
