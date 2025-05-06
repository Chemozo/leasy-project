from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib import messages

class CustomLoginView(LoginView):
    template_name = "users/login.html"
    redirect_authenticated_user = True
    def form_invalid(self, form):
        messages.error(self.request, "Correo o contraseña incorrectos.")
        return super().form_invalid(form)

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("login")
