# Red Social de Aficiones

Mini red social temática construida con Django. Los usuarios pueden compartir publicaciones (texto + imagen), seguir a otros, dar likes, comentar y recibir notificaciones.

## Stack

- **Backend**: Django (Python) + SQLite (dev) / Postgres (prod opcional)
- **Frontend**: HTML + CSS (tema Claude: paleta crema + coral terracota, tipografía serif/sans) + JS vanilla
- **Imágenes**: Cloudinary en producción, FileSystemStorage en local
- **Servidor estáticos**: WhiteNoise
- **Deploy**: Render

## Funcionalidades

- Registro, login, logout
- Publicaciones con texto e imagen (crear, ver)
- Seguir / dejar de seguir usuarios
- Muro con publicaciones de seguidos
- Likes y comentarios
- Notificaciones (like / comment / follow) con badge en navbar y polling cada 30s
- Carga asincrónica del feed (infinite scroll)
- Landing pública con video de fondo

## Setup local

```bash
# 1) Clonar y entrar
git clone https://github.com/IzaguirreCarlos/red_social_aficiones.git
cd red_social_aficiones

# 2) Crear venv e instalar
python -m venv venv
source venv/bin/activate              # Linux/WSL/macOS
# .\venv\Scripts\Activate.ps1         # Windows PowerShell
pip install -r requirements.txt

# 3) Variables de entorno (copia y edita)
cp .env.example .env

# 4) Base de datos
python manage.py migrate
python manage.py createsuperuser      # opcional

# 5) Arrancar
python manage.py runserver
```

Abre `http://127.0.0.1:8000/`.

## Estructura

```
config/         settings, urls raíz, wsgi/asgi
accounts/       app de autenticación (User extendido vía Profile)
posts/          app principal (Post, Comment, Like, Follow, Notification + signals)
templates/      base.html, landing.html, includes
static/         css/styles.css (tema Claude), js/app.js
```

## URLs principales

| Ruta | Descripción |
|---|---|
| `/` | Landing pública con video |
| `/accounts/login/` | Iniciar sesión |
| `/accounts/register/` | Crear cuenta |
| `/posts/` | Muro (requiere login) |
| `/posts/create/` | Publicar |
| `/posts/explore/` | Explorar y seguir usuarios |
| `/posts/notifications/` | Notificaciones |
| `/admin/` | Django admin |

## Deploy a Render

1. Conecta el repo en Render.
2. Crea un Web Service con build command `bash build.sh` y start command `gunicorn config.wsgi`.
3. Setea las variables del `.env.example` en Render.
4. Para imágenes en producción configura Cloudinary (`CLOUDINARY_*`).

## Licencia

Proyecto educativo.
