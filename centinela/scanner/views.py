from time import timezone
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.urls import reverse
from .forms import CustomUserCreationForm  # Importar nuestro formulario personalizado



def index_view(request):
    return render(request, 'index.html')

def auth_view(request):
    # Si el usuario ya está autenticado, redirigir a la página principal
    if request.user.is_authenticated:
        return redirect('index_view')
    return render(request, 'auth.html')

class LoginViewCustom(LoginView):
    template_name = 'auth.html'

    def form_valid(self, form):
        """Se ejecuta si el login es válido"""
        remember_me = self.request.POST.get('remember_me')
        if not remember_me:
            # Expira la sesión al cerrar el navegador
            self.request.session.set_expiry(0)

        # Mensaje de bienvenida al logear
        messages.success(self.request, "Inicio de sesión exitoso!")
        
        return super().form_valid(form)

    def get_success_url(self):
        # Redirige al home o al next param si existe
        return self.get_redirect_url() or '/'

def register_view(request):
    # Si el usuario ya está autenticado, redirigir al home
    if request.user.is_authenticated:
        return redirect('index_view')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # guarda el usuario
            login(request, user)  # inicia sesión automáticamente
            messages.success(request, '¡Registro exitoso! Bienvenido.')
            return redirect('index_view')
        else:
            # Itera sobre todos los errores del formulario y los agrega a messages
            for error_list in form.errors.values():
                for error in error_list:
                    messages.error(request, error)
            return redirect(reverse('auth_view') + '?form=register')

    # Si es GET, redirigir a la página de autenticación con el formulario de registro
    return redirect(reverse('auth_view') + '?form=register')

def logout_view(request):
    logout(request)
    return redirect('auth_view')