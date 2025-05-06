from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView  # Add this import

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
#    path("", include("reports.urls")),
    path("", RedirectView.as_view(url="/users/login/")),
]
