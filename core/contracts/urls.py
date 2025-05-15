from django.urls import path
from .views import ContractListView, ContractCreateView

urlpatterns = [
    path("", ContractListView.as_view(), name="contract_list"),
    path("create/", ContractCreateView.as_view(), name="contract_create"),
]
