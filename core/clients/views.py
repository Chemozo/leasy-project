from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.db.models import Q, Exists, OuterRef
from .models import Client
from contracts.models import Contract  #
from .forms import ClientForm


class ClientListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Client
    template_name = "clients/client_list.html"
    context_object_name = "clients"
    permission_required = "clients.view_client"
    paginate_by = 20

    def get_queryset(self):
        queryset = Client.objects.annotate(
            has_active_contract=Exists(
                Contract.objects.filter(client=OuterRef("pk"), active=True)
            )
        )

        search_query = self.request.GET.get("q")
        if search_query:
            return queryset.filter(
                Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
                | Q(document_number__icontains=search_query)
            )
        return queryset


class ClientCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    permission_required = "clients.add_client"
    template_name = "clients/client_create.html"
    success_url = reverse_lazy("client_list")

    def form_valid(self, form):
        if Client.objects.filter(
            document_number=form.instance.document_number
        ).exists():
            form.add_error(
                "document_number", "A client with this document number already exists"
            )
            return self.form_invalid(form)
        return super().form_valid(form)
