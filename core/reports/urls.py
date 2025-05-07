from django.urls import path
from .views import DashboardView

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("", DashboardView.as_view()),  # Root URL now points to dashboard
]