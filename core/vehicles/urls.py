from django.urls import path
from .views import (
    VehicleListView,
    VehicleCreateView,
    VehicleBrandCreateView,
    VehicleModelCreateView,
)

urlpatterns = [
    path("", VehicleListView.as_view(), name="vehicle_list"),
    path("new/", VehicleCreateView.as_view(), name="vehicle_create"),
    path("brand/new/", VehicleBrandCreateView.as_view(), name="vehicle_brand_create"),
    path("model/new/", VehicleModelCreateView.as_view(), name="vehicle_model_create"),
]
