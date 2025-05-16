from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.db import models
from django.db.models import F, Max, ExpressionWrapper, DurationField, Exists, OuterRef
from django.db.models.functions import Cast
from django.utils import timezone
from .models import Vehicle, VehicleBrand, VehicleModel
from contracts.models import Contract
from .forms import VehicleForm, VehicleBrandForm, VehicleModelForm


class VehicleListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Vehicle
    template_name = "vehicles/vehicle_list.html"
    context_object_name = "vehicles"
    permission_required = "vehicles.view_vehicle"
    paginate_by = 20

    def get_queryset(self):
        active_contract_exists = Contract.objects.filter(
            vehicle=OuterRef("pk"), active=True
        )
        return Vehicle.objects.annotate(
            has_active_contract=Exists(active_contract_exists),
            last_contract_end=Max("contracts__end_date"),
            days_since_last_contract=ExpressionWrapper(
                Cast(timezone.now(), output_field=models.DateField())
                - Cast(F("last_contract_end"), output_field=models.DateField()),
                output_field=DurationField(),
            ),
        )


class VehicleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Vehicle
    form_class = VehicleForm  # <-- use the custom form
    template_name = "vehicles/vehicle_create.html"
    permission_required = "vehicles.add_vehicle"
    success_url = reverse_lazy("vehicle_list")

    def form_valid(self, form):
        # Validate unique plate/VIN
        if Vehicle.objects.filter(license_plate=form.instance.license_plate).exists():
            form.add_error("license_plate", "A vehicle with this plate already exists")
            return self.form_invalid(form)
        if form.instance.vin and Vehicle.objects.filter(vin=form.instance.vin).exists():
            form.add_error("vin", "A vehicle with this VIN already exists")
            return self.form_invalid(form)
        return super().form_valid(form)


class VehicleBrandCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = VehicleBrand
    form_class = VehicleBrandForm
    template_name = "vehicles/vehicle_brand_create.html"
    permission_required = "vehicles.add_vehiclebrand"
    success_url = reverse_lazy("vehicle_list")


class VehicleModelCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = VehicleModel
    form_class = VehicleModelForm
    template_name = "vehicles/vehicle_model_create.html"
    permission_required = "vehicles.add_vehiclemodel"
    success_url = reverse_lazy("vehicle_list")
