import os
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.conf import settings
from django.core.paginator import Paginator
from django_rq import enqueue
from .tasks import generate_report_task
import pandas as pd
from openpyxl import load_workbook
from datetime import datetime

from clients.models import Client
from vehicles.models import Vehicle
from contracts.models import Contract

MAX_FILE_SIZE = 5 * 1024 * 1024
REQUIRED_CLIENT_COLUMNS = {"Nombres", "Apellidos", "Número de documento"}
REQUIRED_VEHICLE_COLUMNS = {"Marca del auto", "Modelo del auto", "Placa del auto"}


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "reports/dashboard.html"

    def post(self, request, *args, **kwargs):
        if "generate_report" in request.POST:
            # Handle report generation
            selected_columns = request.POST.getlist("selected_columns")
            if not selected_columns:
                messages.error(request, "Please select at least one column.")
                return redirect("dashboard")

            data = request.session.get("uploaded_data", [])
            enqueue(generate_report_task, request.user.email, selected_columns, data)
            messages.success(
                request, "Report is being generated. You'll receive an email shortly."
            )
            return redirect("dashboard")

        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            messages.error(request, "No file selected!")
            return redirect("dashboard")

        if not uploaded_file.name.endswith((".xlsx", ".csv")):
            messages.error(request, "Invalid file format. Only .xlsx/.csv allowed.")
            return redirect("dashboard")

        if uploaded_file.size > MAX_FILE_SIZE:
            return self.process_large_file(uploaded_file, request)

        try:
            if uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file, engine="openpyxl")
            else:
                df = pd.read_csv(uploaded_file)

            missing_client_cols = REQUIRED_CLIENT_COLUMNS - set(df.columns)
            missing_vehicle_cols = REQUIRED_VEHICLE_COLUMNS - set(df.columns)

            if missing_client_cols:
                messages.error(
                    request, f"Missing client columns: {', '.join(missing_client_cols)}"
                )
                return redirect("dashboard")
            if missing_vehicle_cols:
                messages.error(
                    request,
                    f"Missing vehicle columns: {', '.join(missing_vehicle_cols)}",
                )
                return redirect("dashboard")

            request.session["uploaded_data"] = df.to_dict("records")
            messages.success(request, "File uploaded successfully!")

            self.save_to_database(df.to_dict("records"))

        except Exception as e:
            messages.error(request, f"Error processing file: {str(e)}")

        return redirect("dashboard")

    def process_large_file(self, file, request):
        try:
            temp_path = os.path.join(settings.MEDIA_ROOT, "temp", file.name)
            with open(temp_path, "wb+") as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            sample = pd.read_csv(temp_path, nrows=100)
            missing_client_cols = REQUIRED_CLIENT_COLUMNS - set(sample.columns)
            missing_vehicle_cols = REQUIRED_VEHICLE_COLUMNS - set(sample.columns)

            if missing_client_cols:
                messages.error(
                    request, f"Missing client columns: {', '.join(missing_client_cols)}"
                )
                return redirect("dashboard")
            if missing_vehicle_cols:
                messages.error(
                    request,
                    f"Missing vehicle columns: {', '.join(missing_client_cols)}",
                )
                return redirect("dashboard")

            bytes_per_row = sample.memory_usage(index=False, deep=True).sum() / len(
                sample
            )

            chunk_size = int(MAX_FILE_SIZE // bytes_per_row)

            for chunk in pd.read_csv(temp_path, chunksize=chunk_size):

                chunk.memory_usage(index=False, deep=True) / chunk.shape[0]

                self.save_to_database(chunk.to_dict("records"))

            messages.debug(request, "Large file processed in batches!")
            messages.success(request, "File uploaded successfully!")

            os.remove(temp_path)  # Cleanup
        except Exception as e:
            messages.error(request, f"Batch processing failed: {str(e)}")
        return redirect("dashboard")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["username"] = self.request.user.email.split("@")[0]

        data = self.request.session.get("uploaded_data", [])

        paginator = Paginator(data, 20)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        if data:
            context["columns"] = page_obj.object_list[0].keys()  # Extract column names
            context["data"] = page_obj.object_list
        context["page_obj"] = page_obj

        return context

    def save_to_database(self, data):
        # Step 1: Bulk create Clients
        new_clients = [
            Client(
                document_number=row["Número de documento"],
                first_name=row["Nombres"],
                last_name=row["Apellidos"],
            )
            for row in data
        ]
        Client.objects.bulk_create(new_clients, ignore_conflicts=True)

        # Step 2: Bulk create Vehicles
        new_vehicles = [
            Vehicle(
                license_plate=row["Placa del auto"],
                brand=row["Marca del auto"],
                model=row["Modelo del auto"],
            )
            for row in data
        ]
        Vehicle.objects.bulk_create(new_vehicles, ignore_conflicts=True)

        # Step 3: Refresh Client and Vehicle references
        document_numbers = {str(row["Número de documento"]) for row in data}
        license_plates = {row["Placa del auto"] for row in data}

        clients = {
            client.document_number: client
            for client in Client.objects.filter(document_number__in=document_numbers)
        }
        vehicles = {
            vehicle.license_plate: vehicle
            for vehicle in Vehicle.objects.filter(license_plate__in=license_plates)
        }

        # Step 4: Prepare Contracts
        new_contracts = []
        assigned_vehicles = set()
        assigned_clients = set()
        for row in data:
            client = clients.get(str(row["Número de documento"]))
            vehicle = vehicles.get(row["Placa del auto"])

            if not client or not vehicle:
                continue

            if Contract.objects.filter(client=client, active=True).exists():
                continue
            if Contract.objects.filter(vehicle=vehicle, active=True).exists():
                continue

            if vehicle.id in assigned_vehicles:
                continue
            if client.id in assigned_clients:
                continue

            try:
                start_date = datetime.strptime(
                    row["Inicio de contrato"], "%m/%d/%Y"
                ).date()
                end_date = datetime.strptime(row["Fin de contrato"], "%m/%d/%Y").date()
            except ValueError as e:
                print("Skipping row: date error", row, e)
                continue

            new_contracts.append(
                Contract(
                    client=client,
                    vehicle=vehicle,
                    billing_cycle=row["Periodo de pago"],
                    installment_amount=row["Cuota semanal"],
                    start_date=start_date,
                    end_date=end_date,
                    active=row["Activo"],
                )
            )
            assigned_vehicles.add(vehicle.id)
            assigned_clients.add(client.id)

        # Step 5: Bulk create Contracts
        Contract.objects.bulk_create(new_contracts)
