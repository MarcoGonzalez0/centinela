# Nombre del proyecto
Centinela

## Descripción

Aplicación Django con API REST para escaneo automatizado de vulnerabilidades web: Nmap, headers HTTP, SSL/TLS, WHOIS, DNS y Google Dorks.

## Características

El sistema recibe la dirección de una página web, analiza los módulos seleccionados y responde de manera no bloqueante con el módulo que termina primero, esto se hace con Celery y Redis, el sistema también cuenta con autenticación, gestión y persistencia de usuarios y escaneos, integrado con análisis con IA (Deepseek), generación de reportes PDF y gráficos estilizados JS.

## Tecnologías usadas

- Procesamiento asíncrono a través de Celery y Redis, permitiendo múltiples escaneos en segundo plano sin bloquear el servidor web.
- Backend desarrollado con Django.
- Frontend desarrollado con Django templates.
- Base de datos relacional MySQL para la persistencia de datos.
- Arquitectura modular con escáneres independientes y fácilmente integrables.
- Despliegue en contenedor Docker y sincronización en Docker Compose.

## Instalación

### Requisitos
- Docker
- Docker Compose

### 1. Clonar repositorio

```bash
git clone https://github.com/MarcoGonzalez0/centinela.git
cd centinela
cd centinela
```

### 2. Configurar variables de entorno

Renombrar `.env.example` a `.env`
y completar las variables necesarias.

```bash
cp .env.example .env
```


### 3. Levantar el proyecto

```bash
docker compose up --build
```

El sistema automáticamente:
- espera MySQL y Redis
- aplica migraciones
- crea el superusuario admin
- inicia Django y Celery
  
## Acceso

- Django: http://localhost:8000
- Registrarse y utilizar

## Uso

Para profesionales y estudiantes del área de ciberseguridad, empresas o particulares que quieran verificar la exposisción y vulnerabilidad de sus servicios.

## Autor

Marco González
