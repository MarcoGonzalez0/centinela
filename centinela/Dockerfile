# Usa Python oficial
FROM python:3.11-slim

# Configuración básica
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Copiar wait-for-it
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Instala dependencias del sistema (ej. para nmap, MySQL, etc.)
RUN apt-get update && apt-get install -y \
    gcc \
    libmariadb-dev-compat \
    libmariadb-dev \
    nmap \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements primero (para caché)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Copiar el script de entrada
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# Expone puerto de Django
EXPOSE 8000

# Comando por defecto: Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
