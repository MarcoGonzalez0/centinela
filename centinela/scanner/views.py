#Standard Library
from time import timezone

#Django
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.urls import reverse

from scanner.tasks import run_modulo_task

#Forms
from .forms import CustomUserCreationForm, ScanForm  # Importar nuestro formulario personalizado

#Models
from .models import Escaneo, resultadoModulo


def index_view(request): # el escaneo se hace aqui
    if request.method == 'POST':
        if request.user.is_authenticated: # si es post y el usuario está autenticado
            form = ScanForm(request.POST) # ocupamos el formulario predefinido en forms.py
            if form.is_valid():
                target = form.cleaned_data['target']
                modules = form.cleaned_data['modules']

                print(modules) # DEBUG
                try:
                    
                    """
                    -------FLUJO--------
                    1. Crear instancia de Escaneo en estado 'pendiente'
                    2. Para cada módulo seleccionado, crear instancia de resultadoModulo en estado 'pendiente' con referencia al Escaneo
                    3. Iniciar tareas asíncronas (usando Celery) para ejecutar cada módulo
                    4. Cada tarea actualiza el estado del resultadoModulo y guarda resultados
                    5. Cuando termine un módulo se guarda en la base de datos y de alguna manera se da aviso de que tal modulo terminó
                    6. Con ese aviso, en el index, se renderiza el resultado de ese módulo con el visuals .html correspondiente
                    7. Cuando todos los módulos de un escaneo terminan, actualizar el estado del Escaneo a 'completado'
                    -------------------
                    """

                    # 1. Crear instancia de Escaneo
                    escaneo = Escaneo.objects.create(
                        user=request.user,
                        objetivo=target,
                        tipo_objetivo='dominio' if not target.replace('.', '').isdigit() else 'ip',
                        estado='en_proceso'
                    )

                    # 2. Crear instancias de resultadoModulo
                    for modulo in modules:
                        
                        resultado = resultadoModulo.objects.create(
                            escaneo=escaneo, # Foranea al escaneo creado
                            nombre_modulo=modulo,
                            estado='pendiente',
                            resultado={}
                        )
                        # 3. Iniciar tarea asíncrona
                        if modulo.lower() == "nmap": # nmap es pesado, va en cola heavy
                            run_modulo_task.apply_async(args=[resultado.id], queue="heavy") 
                        else: # el resto va en cola default
                            run_modulo_task.delay(resultado.id) # Llamada asíncrona con Celery

                    messages.success(request, f'Scan iniciado para {target} con módulos: {", ".join(modules)}')

                    
                    # Cuando las tareas terminen en tasks.py, de alguna manera mostrar los resultados en el index sin recargar

                    return redirect(f'{reverse("index_view")}?escaneo_id={escaneo.id}')  # Redirigir a la misma página con el ID del escaneo

                except Exception as e:
                    # este error se maneja en messages (se muestra arriba)
                    messages.error(request, f'Error al iniciar el scan: {e}')            

            # los errores del formulario se manejan automaticamente en form.errors
        else:
            # POST pero sin autenticación → mostrar aviso
            messages.info(request, 'Por favor, inicia sesión para realizar escaneos.')
            form = ScanForm(request.POST)  # para mantener datos escritos
    else:
        form = ScanForm()  # Crear formulario vacío para GET

    escaneo_id = request.GET.get('escaneo_id') # Obtener el ID del escaneo de los parámetros GET
    return render(request, 'index.html', {'form': form, 'escaneo_id': escaneo_id}) # si es GET, solo renderiza la página



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

# Para renderizar los visuals de cada módulo, esto es para fragmentos que ocupen django
def module_visual(request, name):
    return render(request, f"modules/{name}_visuals.html")