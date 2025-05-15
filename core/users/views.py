from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.contrib.auth.views import LogoutView
from .forms import CustomLoginForm


class CustomLogoutView(LogoutView):
    next_page = "login"


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = "users/login.html"
    redirect_authenticated_user = True

    def form_invalid(self, form):
        messages.error(self.request, "Correo o contraseña incorrectos.")
        return super().form_invalid(form)
