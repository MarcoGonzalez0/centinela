FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libmariadb-dev-compat \
    libmariadb-dev \
    nmap \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python (esto se cachea si requirements.txt no cambia)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar solo scripts necesarios
COPY wait-for-it.sh /wait-for-it.sh
COPY entrypoint.sh /entrypoint.sh

RUN sed -i 's/\r$//' /wait-for-it.sh /entrypoint.sh \
    && chmod +x /wait-for-it.sh /entrypoint.sh

# ❌ NO COPIAR TODO EL CÓDIGO AQUÍ
# COPY . .  <- ELIMINAR ESTA LÍNEA

EXPOSE 8000

ENTRYPOINT ["sh", "/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]