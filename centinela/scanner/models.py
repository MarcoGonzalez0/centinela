from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Escaneo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='escaneos') #foranea a usuario predefinido por django
    objetivo = models.CharField(max_length=100)                                       #educativa.ipchile.cl o 192.168.1.1
    tipo_objetivo = models.CharField(max_length=7)                                    #dominio/ip
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(auto_now=True)
    estado = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
        ('error', 'Error')
    ], default='pendiente')

    def __str__(self):
        return f"Escaneo by {self.user.username} on {self.fecha_inicio.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        verbose_name = 'Escaneo'
        verbose_name_plural = 'Escaneos'
        ordering = ['-fecha_inicio']  # Order by start date descending

class resultadoModulo(models.Model):
    escaneo = models.ForeignKey(Escaneo, on_delete=models.CASCADE, related_name='resultados') #foranea, 1 resultado pertenece a 1 escaneo
    nombre_modulo = models.CharField(max_length=12)                                           # nmap, dorks, etc
    estado = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
        ('error', 'Error')
    ], default='pendiente')
    resultado = models.JSONField()  # JSON del resultado
    fecha_ejecucion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resultado for {self.nombre_modulo} in Escaneo {self.escaneo.id}"

    class Meta:
        verbose_name = 'Resultado de Módulo'
        verbose_name_plural = 'Resultados de Módulos'
        ordering = ['escaneo', 'modulo']  # Order by escaneo and then by module name