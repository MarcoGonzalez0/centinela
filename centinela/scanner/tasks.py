# Transaction
from django.db import transaction
# Celery
from celery import shared_task
# Modelos
from .models import resultadoModulo, Escaneo
#Escaneos
from modulos.scan_dns import run_dns
from modulos.scan_dorks import run_dorks
from modulos.scan_headerhttp import run_headerhttp
from modulos.scan_nmap import run_nmap
from modulos.scan_ssl import run_ssl
from modulos.scan_whois import run_whois


@shared_task
def run_modulo_task(resultado_id):
    try:
        # Obtener el resultadoModulo y actualizar estado a "en_proceso"
        resultado = resultadoModulo.objects.get(id=resultado_id)
        resultado.estado = "en_proceso"
        resultado.save()

        # Simulación de ejecución del módulo
        # Logica para ejecutar el módulo específico

         # Diccionario de funciones disponibles
        modulos_disponibles = {
            'dns': run_dns,
            'dorks': run_dorks,
            'headerhttp': run_headerhttp,
            'nmap': run_nmap,
            'ssl': run_ssl,
            'whois': run_whois
        }

        # Ejecutar el módulo correspondiente
        funcion_modulo = modulos_disponibles.get(resultado.nombre_modulo)
        if not funcion_modulo:
            raise ValueError(f"Módulo desconocido: {resultado.nombre_modulo}")
        
        resultados_modulo = funcion_modulo(resultado.escaneo.objetivo)

        resultado.resultado = resultados_modulo
        resultado.estado = "completado"
        resultado.save()

        # Chequear si ya todos los módulos de este escaneo terminaron
        escaneo = resultado.escaneo
        if not escaneo.resultadomodulo_set.filter(estado__in=["pendiente", "en_proceso"]).exists():
            escaneo.estado = "completado"
            escaneo.save()

    except Exception as e:
        try:
            with transaction.atomic():
                resultado = resultadoModulo.objects.get(id=resultado_id)
                resultado.estado = "error"
                resultado.resultado = {"error": str(e)}
                resultado.save()

                # También actualizar el estado del escaneo principal a "en_proceso"
                escaneo = resultado.escaneo
                if not escaneo.resultadomodulo_set.filter(estado__in=["pendiente", "en_proceso"]).exists():
                    escaneo.estado = "completado"
                    escaneo.save()
                    
        except Exception as ex:
            # Manejo de errores en la transacción
            print(f"Error al actualizar el estado del resultado o escaneo: {ex}")
