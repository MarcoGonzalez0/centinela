#Standard Library
import io
from time import sleep, timezone
import json
from datetime import datetime

#Django
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.urls import reverse

#reportlabs para PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors

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
                            sleep(1.2) # Simulamos retardo para pruebas
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

    # Manejo de GET redirigido con ?escaneo_id=xxxx
    escaneo_id = request.GET.get('escaneo_id') # Obtener el ID del escaneo de los parámetros GET
    escaneo = None

    if escaneo_id:
        try:
            escaneo = Escaneo.objects.get(id=escaneo_id, user=request.user)
        except Escaneo.DoesNotExist:
            messages.error(request, 'Escaneo no encontrado o no tienes permiso para verlo.')
            escaneo = None
    return render(request, 'index.html', {'form': form, 
                                          'escaneo_id': escaneo_id, 
                                          'escaneo': escaneo
    }) # si es GET, solo renderiza la página



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
    return render(request, f"modules/{name}")

def scan_report_view(request, escaneo_id):
    try:
        # Obtener escaneo y sus resultados
        escaneo = get_object_or_404(Escaneo, id=escaneo_id)
        resultados = resultadoModulo.objects.filter(escaneo=escaneo)

        # Crear un buffer de memoria
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Margen superior inicial
        y = height - inch

        # Encabezado
        p.setFont("Helvetica-Bold", 16)
        p.drawString(1 * inch, y, f"Informe de Escaneo #{escaneo.id}")
        y -= 0.4 * inch
        p.setFont("Helvetica", 11)
        p.drawString(1 * inch, y, f"Objetivo: {escaneo.objetivo}")
        y -= 0.25 * inch
        p.drawString(1 * inch, y, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        y -= 0.5 * inch

        # Línea separadora
        p.setStrokeColor(colors.grey)
        p.line(1 * inch, y, width - inch, y)
        y -= 0.4 * inch

        # Contenido de los resultados
        for r in resultados:
            p.setFont("Helvetica-Bold", 12)
            p.drawString(1 * inch, y, f"Módulo: {r.nombre_modulo}")
            y -= 0.2 * inch

            p.setFont("Helvetica", 10)
            p.drawString(1 * inch, y, f"Estado: {r.estado.capitalize()}")
            y -= 0.2 * inch

            # Convertir JSON a texto legible (solo lo esencial)
            resultado_texto = json.dumps(r.resultado, indent=2, ensure_ascii=False)
            for linea in resultado_texto.split("\n"):
                if y < 1 * inch:  # Crear nueva página si no hay espacio
                    p.showPage()
                    y = height - inch
                p.drawString(1.2 * inch, y, linea[:100])  # recorta líneas largas
                y -= 0.18 * inch

            y -= 0.3 * inch
            p.line(1 * inch, y, width - inch, y)
            y -= 0.4 * inch

        # Finalizar PDF
        p.showPage()
        p.save()
        buffer.seek(0)

        # Preparar respuesta HTTP
        filename = f"escaneo_{escaneo.id}_informe.pdf"
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except Exception as e:
        messages.error(request, f'Error al generar el informe: {e}')
        return redirect('index_view')
    

def escaneo_status_view(request, escaneo_id):
    escaneo = Escaneo.objects.get(id=escaneo_id, user=request.user)
    return JsonResponse({
        "estado": escaneo.estado,
        "id": escaneo.id
    })