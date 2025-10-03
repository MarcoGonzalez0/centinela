#!/bin/sh
# entrypoint.sh

# Esperar a MySQL
echo "Esperando a MySQL..."
/wait-for-it.sh db:3306 --timeout=30 --strict -- echo "MySQL listo"

# Esperar a Redis
echo "Esperando a Redis..."
/wait-for-it.sh redis:6379 --timeout=30 --strict -- echo "Redis listo"

# Aplicar migraciones de Django
# Antes de esto aplica makemigrations para que aqui solo lea el archivo generado
echo "Aplicando migraciones de Django..."
python manage.py migrate --noinput

# Crear superusuario solo si no existe (opcional)
# python manage.py createsuperuser --noinput || true

echo "Iniciando servidor Django..."
exec "$@"
