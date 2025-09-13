from time import timezone
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.urls import reverse
from .forms import CustomUserCreationForm, ScanForm  # Importar nuestro formulario personalizado



def index_view(request): #el escaneo se hace aqui
    if request.method == 'POST': #si es post, es decir, se envió el formulario
        form = ScanForm(request.POST) #ocupamos el formulario predefinido en forms.py
        if form.is_valid():
            target = form.cleaned_data['target']
            modules = form.cleaned_data['modules']
            try:
                # Aquí puedes manejar el escaneo con los módulos seleccionados
                messages.success(request, f'Scan iniciado para {target} con módulos: {", ".join(modules)}')

                # con el target mandarlo a los modulos seleccionados tipo run_nmap(target) etc
                
                return redirect('index_view')

            except Exception as e:
                #este error se maneja en messages (se muestra arriba)
                messages.error(request, f'Error al iniciar el scan: {e}')            
        
        #los errores del formulario se manejan automaticamente en form.errors
    else:
        form = ScanForm()  # Crear formulario vacío para GET

    return render(request, 'index.html', {'form': form}) #si es get, solo renderiza la pagina

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
    
    #si el login no es válido
    def form_invalid(self, form):
        #errores se manejan en form.errors
        return super().form_invalid(form)

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
            #Errores se manejan en form.errors
            return redirect(reverse('auth_view') + '?form=register')

    # Si es GET, redirigir a la página de autenticación con el formulario de registro
    return redirect(reverse('auth_view') + '?form=register')

def logout_view(request):
    logout(request)
    return redirect('auth_view')