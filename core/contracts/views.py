from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.db.models import (
    Q,
    F,
    Count,
    Sum,
    Case,
    When,
    Value,
    IntegerField,
    ExpressionWrapper,
    DurationField,
    Max,
    Min,
    DateField,
)
from django.db.models.functions import Coalesce, Now, Cast
from django.utils import timezone
from django import forms
from .models import Contract, Client, Vehicle
from invoices.models import Invoice
from .forms import ContractCreateForm


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
                pending_invoices=Count(
                    "invoices", filter=Q(invoices__status=Invoice.StatusChoices.PENDING)
                ),
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
                oldest_pending_issue_date=Min(
                    "invoices__issue_date",
                    filter=Q(invoices__status=Invoice.StatusChoices.PENDING),
                ),
            )
            .annotate(
                days_since_oldest_pending_invoice=ExpressionWrapper(
                    Cast(Now(), output_field=DateField())
                    - Coalesce(
                        F("oldest_pending_issue_date"),
                        Cast(Now(), output_field=DateField()),
                    ),
                    output_field=DurationField(),
                )
            )
            .annotate(
                days_since_oldest_pending_invoice_int=Cast(
                    F("days_since_oldest_pending_invoice"), IntegerField()
                )
            )
            .distinct()
        )

        return queryset


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

        form.instance.active = True
        return super().form_valid(form)


class ContractCreateForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ["client", "vehicle", "billing_cycle", "installment_amount"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].queryset = Client.objects.filter(
            ~Q(contracts__active=True)
        )
        self.fields["vehicle"].queryset = Vehicle.objects.filter(
            ~Q(contracts__active=True)
        )
