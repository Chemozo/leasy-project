from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
    path("", include("reports.urls")),
    path("contracts/", include("contracts.urls")),
    path("clients/", include("clients.urls")),
    path("vehicles/", include("vehicles.urls")),
]
