#!/bin/sh
# entrypoint.sh

# Esperar a MySQL
echo "Esperando a MySQL..."
/wait-for-it.sh db:3306 --timeout=120 --strict -- echo "MySQL listo"

# Esperar a Redis
echo "Esperando a Redis..."
/wait-for-it.sh redis:6379 --timeout=90 --strict -- echo "Redis listo"

if [ "$ROLE" = "worker" ]; then
    echo "Iniciando Celery Worker..."
    exec "$@"
else
    # Aplicar migraciones de Django (solo para web)
    echo "Aplicando migraciones de Django..."
    python manage.py migrate --noinput
    
    echo "Iniciando servidor Django..."
    exec "$@"
fi