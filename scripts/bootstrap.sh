#!/usr/bin/env bash
# Prepara el entorno local: aplica migraciones y crea el superusuario admin/admin.
# Requiere que los servicios esten levantados (docker compose up -d).
set -euo pipefail

docker compose exec -T bjj-library python3 manage.py migrate --noinput

docker compose exec -T bjj-library python3 manage.py shell <<'PY'
from django.contrib.auth import get_user_model

User = get_user_model()
if User.objects.filter(username='admin').exists():
    print('El superusuario admin ya existe.')
else:
    User.objects.create_superuser('admin', 'admin@gmail.com', 'admin', 'admin', password='admin')
    print('Superusuario admin creado (password: admin).')
PY
