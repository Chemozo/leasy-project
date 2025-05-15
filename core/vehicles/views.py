from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.db.models import F, Max, ExpressionWrapper, DurationField
from django.utils import timezone
from .models import Vehicle


class VehicleListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Vehicle
    template_name = "vehicles/vehicle_list.html"
    context_object_name = "vehicles"
    permission_required = "vehicles.view_vehicle"
    paginate_by = 20

    def get_queryset(self):
        return Vehicle.objects.annotate(
            last_contract_end=Max("contracts__end_date"),
            days_since_last_contract=ExpressionWrapper(
                timezone.now() - F("last_contract_end"), output_field=DurationField()
            ),
        )


class VehicleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Vehicle
    template_name = "vehicles/vehicle_create.html"
    fields = ["brand", "model", "plate", "vin"]
    permission_required = "vehicles.add_vehicle"
    success_url = reverse_lazy("vehicle_list")

    def form_valid(self, form):
        # Validate unique plate/VIN
        if Vehicle.objects.filter(plate=form.instance.plate).exists():
            form.add_error("plate", "A vehicle with this plate already exists")
            return self.form_invalid(form)
        if form.instance.vin and Vehicle.objects.filter(vin=form.instance.vin).exists():
            form.add_error("vin", "A vehicle with this VIN already exists")
            return self.form_invalid(form)
        return super().form_valid(form)


class BrandCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Vehicle.brand
    template_name = "vehicles/brand_create.html"
    fields = ["name"]
    permission_required = "vehicles.add_brand"
    success_url = reverse_lazy("vehicle_create")


class ModelCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Vehicle.model
    template_name = "vehicles/model_create.html"
    fields = ["name", "brand"]
    permission_required = "vehicles.add_model"
    success_url = reverse_lazy("vehicle_create")
