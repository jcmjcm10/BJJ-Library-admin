# BJJ Library

API REST en Django para catalogar vídeos de Brazilian Jiu-Jitsu alojados en YouTube, etiquetarlos y organizarlos en listas ordenadas por usuario.

![Captura](docs/screenshot.png)

## Características

- CRUD de vídeos identificados por su ID de YouTube, con propietario y visibilidad (`private` / `public`).
- Filtrado por visibilidad: cada usuario ve sus propios vídeos más los marcados como públicos.
- Etiquetas (`Tag`) y asociación vídeo–etiqueta (`VideoTag`); el serializador de vídeo devuelve las etiquetas resueltas por nombre.
- Listas de vídeos con orden explícito: alta de vídeo directamente en una lista, e inserción, eliminación y reordenación (subir/bajar) mediante operaciones sobre la lista.
- Autenticación por token con caducidad propia (24 h), implementada sobre `TokenAuthentication` de DRF mediante un mixin aplicado a los ViewSets.
- Login y logout que además invalidan las sesiones activas del usuario y regeneran el token.
- Modelo de usuario propio (`AUTH_USER_MODEL`) con `username`, email, nombre, apellidos e imagen de perfil, y auditoría de cambios vía `django-simple-history`.
- Django Admin con inline de items de lista para gestionar el orden de los vídeos.
- CORS configurable por entorno para consumir la API desde un frontend externo.
- Entorno reproducible con Docker Compose: PostgreSQL 17 + Django, y script de bootstrap que migra y crea el superusuario.

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.12 |
| Framework web | Django 5.2 |
| API | Django REST Framework 3.16 |
| Autenticación | `rest_framework.authtoken` + `ExpiringTokenAutentication` propia |
| Base de datos | PostgreSQL 17 (`psycopg` 3.2) |
| Auditoría | django-simple-history 3.11 |
| CORS | django-cors-headers 4.9 |
| Imágenes | Pillow 12.1 |
| Servidor de aplicación | Gunicorn 23 (4 workers, timeout 60 s) |
| Contenedores | Docker (Ubuntu 24.04) + Docker Compose |

## Puesta en marcha con Docker

Requisitos: Docker y Docker Compose v2 (la plantilla `app.env` usa interpolación de variables dentro del propio fichero de entorno, soportada por versiones recientes de Compose).

1. Clonar el repositorio y situarse en la raíz:

   ```bash
   git clone <url-del-repo> BJJ-Library-admin
   cd BJJ-Library-admin
   ```

2. Crear el fichero de entorno a partir de la plantilla:

   ```bash
   cp app.env-example app.env
   ```

3. Editar `app.env` y sustituir al menos `SECRET_KEY` y `POSTGRES_PASSWORD` por valores propios.

4. Construir y levantar los servicios (PostgreSQL y Django con `runserver`):

   ```bash
   docker compose up -d --build
   ```

5. Aplicar migraciones y crear el superusuario:

   ```bash
   ./scripts/bootstrap.sh
   ```

   El script crea el usuario `admin` con contraseña `admin` si no existe. Cámbiala antes de exponer el servicio.

6. Comprobar que responde:

   - API (root navegable de DRF): http://localhost:8000/
   - Admin de Django: http://localhost:8000/admin/

Para parar el entorno: `docker compose down` (añadir `-v` para borrar también el volumen `pgdata`).

### Otros scripts

- `docker-compose.deploy.yml`: variante que arranca solo el contenedor de la aplicación con Gunicorn (el `CMD` del Dockerfile) y límites de CPU/memoria. Requiere una base de datos accesible y las variables de conexión suministradas aparte.
- `scripts/create_image_tar.sh`: construye la imagen `bjj-library:0.1.0` y la exporta a `bjj-library.tar` con `docker save`.

## Variables de entorno

Se cargan desde `app.env` (fichero no versionado; la plantilla es `app.env-example`).

| Variable | Descripción | Ejemplo |
|---|---|---|
| `POSTGRES_DB` | Nombre de la base de datos que crea el contenedor de PostgreSQL | `bjj_library` |
| `POSTGRES_USER` | Usuario que crea el contenedor de PostgreSQL | `bjj_library` |
| `POSTGRES_PASSWORD` | Contraseña de ese usuario | `changeme` |
| `SECRET_KEY` | Clave secreta de Django. Sin valor por defecto | `changeme-secret-key` |
| `DEBUG` | Modo debug. Activo solo si vale exactamente `True` | `True` |
| `ALLOWED_HOSTS` | Hosts permitidos, separados por comas. Por defecto vacío | `localhost,127.0.0.1` |
| `CSRF_TRUSTED_ORIGINS` | Orígenes de confianza para CSRF, con esquema, separados por comas | `http://localhost:8000` |
| `CORS_ALLOWED_ORIGINS` | Orígenes permitidos por CORS, con esquema, separados por comas | `http://localhost:9000` |
| `CORS_ALLOW_ALL_ORIGINS` | Comodín CORS. Activo solo si vale exactamente `True` | `False` |
| `DB_NAME` | Base de datos a la que conecta Django | `${POSTGRES_DB}` |
| `DB_USERNAME` | Usuario de conexión de Django | `${POSTGRES_USER}` |
| `DB_PASSWORD` | Contraseña de conexión de Django | `${POSTGRES_PASSWORD}` |
| `DB_HOST` | Host de la base de datos (nombre del servicio en Compose) | `db` |
| `DB_PORT` | Puerto de la base de datos | `5432` |

El tiempo de vida del token está fijado en el código: `TOKEN_EXPIRED_AFTER_SECONDS = 86400` en [bjj_library/settings.py](bjj_library/settings.py).

## Endpoints de la API

Las rutas de recursos las genera un `DefaultRouter` de DRF, así que aceptan también la forma de detalle `/<recurso>/<id>/`. La autenticación se envía en la cabecera `Authorization: Token <token>`.

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| `POST` | `/login/` | No | Devuelve token y datos del usuario a partir de `username` y `password`. Regenera el token y borra las sesiones previas |
| `GET` | `/logout/?token=<token>` | No (token por query) | Elimina el token y las sesiones activas de ese usuario |
| `POST` | `/user/` | No | Alta de usuario |
| `GET` | `/video/` | Sí | Vídeos propios más los de visibilidad `public` |
| `POST` | `/video/` | Sí | Crea un vídeo asignándolo al usuario del token. Con `list` en el cuerpo lo añade al final de esa lista |
| `GET` | `/video/<id>/` | Sí | Detalle de un vídeo del queryset visible |
| `PUT` | `/video/<id>/` | Sí | Actualiza `title`, `url` y `youtubeID`, y elimina las etiquetas asociadas al vídeo |
| `DELETE` | `/video/<id>/` | Sí | Borra el vídeo. Solo el propietario o un usuario `is_staff` |
| `GET` | `/Tag/` | Sí | Lista de etiquetas |
| `POST` | `/Tag/` | Sí | Crea una etiqueta |
| `PUT` / `PATCH` / `DELETE` | `/Tag/<id>/` | Sí | Edita o borra una etiqueta |
| `GET` | `/videoTag/` | Sí | Relaciones vídeo–etiqueta |
| `POST` | `/videoTag/` | Sí | Asocia etiqueta a vídeo. Cuerpo: `videoId` y `tagId` |
| `PUT` / `PATCH` / `DELETE` | `/videoTag/<id>/` | Sí | Edita o borra la relación |
| `GET` | `/VideoList/` | Sí | Listas propias y listas sin propietario, con sus vídeos ordenados |
| `POST` | `/VideoList/` | Sí | Crea una lista propiedad del usuario del token |
| `PUT` | `/VideoList/<id>/` | Sí | Operaciones sobre la lista según el campo `op` (ver abajo) |
| `DELETE` | `/VideoList/<id>/` | Sí | Borra la lista. Solo el propietario |
| — | `/admin/` | Sesión Django | Panel de administración |

Operaciones de `PUT /VideoList/<id>/`, con `op` y `video` (id) en el cuerpo:

| `op` | Efecto |
|---|---|
| `insert` | Añade el vídeo al final de la lista. Solo el propietario |
| `remove` | Quita el vídeo y recompacta el campo `order` |
| `up` | Intercambia el orden con el vídeo anterior |
| `down` | Intercambia el orden con el vídeo siguiente |

## Modelos de datos

### `users.User`

Modelo de usuario propio (`AbstractBaseUser` + `PermissionsMixin`), declarado como `AUTH_USER_MODEL`.

| Campo | Tipo | Notas |
|---|---|---|
| `username` | `CharField(255)` | Único. Campo de login |
| `email` | `EmailField(255)` | Único. Obligatorio |
| `name` | `CharField(255)` | Opcional |
| `last_name` | `CharField(255)` | Opcional |
| `image` | `ImageField` | Opcional, se sube a `perfil/` |
| `is_active` | `BooleanField` | Por defecto `True` |
| `is_staff` | `BooleanField` | Por defecto `False` |
| `historical` | `HistoricalRecords` | Historial de cambios (django-simple-history) |

### `api.Video`

| Campo | Tipo | Notas |
|---|---|---|
| `title` | `CharField(128)` | Obligatorio |
| `url` | `CharField(128)` | Obligatorio |
| `youtubeID` | `CharField(16)` | Obligatorio |
| `owner` | `FK → User` | Opcional, `on_delete=PROTECT` |
| `visibility` | `CharField(16)` | Por defecto `private`; el filtrado de lectura compara con `public` |

### `api.Tag`

| Campo | Tipo | Notas |
|---|---|---|
| `name` | `CharField(16)` | Nombre de la etiqueta |

### `api.VideoTag`

Relación N:M entre vídeos y etiquetas.

| Campo | Tipo | Notas |
|---|---|---|
| `video` | `FK → Video` | `on_delete=CASCADE` |
| `tag` | `FK → Tag` | `on_delete=CASCADE` |

### `api.VideoList`

| Campo | Tipo | Notas |
|---|---|---|
| `title` | `CharField(50)` | Obligatorio |
| `videos` | `M2M → Video` | A través de `VideoListItem` |
| `owner` | `FK → User` | Opcional, `on_delete=CASCADE` |

### `api.VideoListItem`

Tabla intermedia que aporta el orden dentro de la lista.

| Campo | Tipo | Notas |
|---|---|---|
| `videoList` | `FK → VideoList` | `on_delete=CASCADE` |
| `video` | `FK → Video` | `on_delete=CASCADE` |
| `order` | `IntegerField` | Por defecto `1`; se asigna como último orden + 1 |

Relaciones resumidas:

```
User 1──N Video          (owner)
User 1──N VideoList      (owner)
Video N──N Tag           (a través de VideoTag)
Video N──N VideoList     (a través de VideoListItem, con order)
```
