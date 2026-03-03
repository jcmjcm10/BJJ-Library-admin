FROM ubuntu:24.04

# Instalamos python y dependencias necesarias
RUN apt-get update && apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    python3-pip

RUN ln -s /usr/bin/python3.12 /usr/bin/python

WORKDIR /app

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN python3.12 -m pip install --break-system-packages -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Coleccionar archivos estáticos (si existen)
RUN python manage.py collectstatic --noinput 2>/dev/null || true

EXPOSE 8000

# Comando para arrancar Gunicorn
CMD ["python3.12", "-m", "gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "60", "bjj_library.wsgi:application"]