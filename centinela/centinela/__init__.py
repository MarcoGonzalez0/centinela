
# Configuración de PyMySQL para usar como MySQLdb
import pymysql
pymysql.install_as_MySQLdb()

# Esto asegura que la aplicación Celery se importe cuando Django se inicie
from .celery import app as celery_app

__all__ = ('celery_app',)