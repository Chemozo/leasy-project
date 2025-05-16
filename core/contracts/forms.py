from django import forms
from django.db.models import Q
from .models import Contract, Client, Vehicle


class ContractCreateForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ["client", "vehicle", "billing_cycle", "installment_amount"]
        widgets = {
            "client": forms.Select(
                attrs={
                    "class": "form-control form-control-lg",
                }
            ),
            "vehicle": forms.Select(
                attrs={
                    "class": "form-control form-control-lg",
                }
            ),
            "billing_cycle": forms.Select(
                attrs={
                    "class": "form-control form-control-lg",
                }
            ),
            "installment_amount": forms.NumberInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "Monto de la cuota",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].queryset = Client.objects.filter(
            ~Q(contracts__active=True)
        )
        self.fields["vehicle"].queryset = Vehicle.objects.filter(
            ~Q(contracts__active=True)
        )
