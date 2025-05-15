from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.db.models import (
    Q,
    F,
    Subquery,
    OuterRef,
    Count,
    Sum,
    Case,
    When,
    Value,
    IntegerField,
)
from django.db.models.functions import ExtractDay
from django.utils import timezone
from django import forms
from .models import Contract, Client, Vehicle
from invoices.models import Invoice


class ContractListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Contract
    template_name = "contracts/contract_list.html"
    context_object_name = "contracts"
    permission_required = "contracts.view_contract"
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            Contract.objects.filter(active=True)
            .select_related("client", "vehicle")
            .annotate(
                # Count pending invoices
                pending_invoices=Count(
                    "invoices", filter=Q(invoices__status=Invoice.StatusChoices.PENDING)
                ),
                # Sum the total pending amount
                total_pending_amount=Sum(
                    Case(
                        When(
                            invoices__status=Invoice.StatusChoices.PENDING,
                            then=F("invoices__amount"),
                        ),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                ),
                # Annotate the raw difference in days
                raw_days_since_latest_invoice=F("invoices__due_date")
                - timezone.now().date(),
            )
        )

        # Add a Python-calculated field for days since the latest invoice
        for contract in queryset:
            if contract.raw_days_since_latest_invoice:
                contract.days_since_latest_invoice = (
                    contract.raw_days_since_latest_invoice.days
                )
            else:
                contract.days_since_latest_invoice = None

        return queryset


class ContractCreateForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ["client", "vehicle", "billing_cycle", "installment_amount"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter clients/vehicles without active contracts
        self.fields["client"].queryset = Client.objects.filter(
            ~Q(contract__active=True)
        )
        self.fields["vehicle"].queryset = Vehicle.objects.filter(
            ~Q(contract__active=True)
        )


class ContractCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    form_class = ContractCreateForm
    template_name = "contracts/contract_create.html"
    permission_required = "contracts.add_contract"
    success_url = reverse_lazy("contract_list")

    def form_valid(self, form):
        # Final validation before saving
        client = form.cleaned_data["client"]
        vehicle = form.cleaned_data["vehicle"]

        if Contract.objects.filter(client=client, active=True).exists():
            form.add_error("client", "Client has an active contract")
            return self.form_invalid(form)

        if Contract.objects.filter(vehicle=vehicle, active=True).exists():
            form.add_error("vehicle", "Vehicle has an active contract")
            return self.form_invalid(form)

        form.instance.active = True  # New contracts are always active
        return super().form_valid(form)
