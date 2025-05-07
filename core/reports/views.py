from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect

import pandas as pd
from openpyxl import load_workbook
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "reports/dashboard.html"
    

    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get("file")
        
        # Validate file
        if not uploaded_file:
            messages.error(request, "No file selected!")
            return redirect("dashboard")
        
        if not uploaded_file.name.endswith((".xlsx", ".csv")):
            messages.error(request, "Invalid file format. Only .xlsx/.csv allowed.")
            return redirect("dashboard")

        # Process file
        try:
            if uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file, engine="openpyxl")
            else:
                df = pd.read_csv(uploaded_file)
                
            # Store data temporarily (we'll use session for demo)
            request.session["uploaded_data"] = df.to_dict("records")
            
            messages.success(request, "File uploaded successfully!")
        except Exception as e:
            messages.error(request, f"Error processing file: {str(e)}")
        
        return redirect("dashboard")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["username"] = self.request.user.email.split("@")[0]
        
        # Get uploaded data from session
        data = self.request.session.get("uploaded_data", [])
        if data:
            context["columns"] = data[0].keys()  # Extract column names
            context["data"] = data
        
        return context