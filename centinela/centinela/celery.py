import os
from celery import Celery

# Establecer el módulo de configuración de Django para el programa 'celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centinela.settings')

# Crear instancia de Celery
app = Celery('centinela')

# Usar una cadena aquí significa que el worker no tiene que serializar
# el objeto de configuración a los procesos hijos.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Cargar módulos de tareas de todas las aplicaciones Django registradas
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')