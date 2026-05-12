# Red Social de Aficiones

Mini red social temática con Django: publicaciones (texto + imagen), follow/unfollow, likes, comentarios y notificaciones.

## Stack

- **Backend**: Django + WhiteNoise (estáticos) + Cloudinary (media en prod)
- **DB**: SQLite en dev, **Postgres en producción** (Neon / Supabase / Vercel Postgres)
- **Frontend**: HTML + CSS (tema Claude) + JS vanilla. Sin frameworks.
- **Deploy**: Vercel (serverless) o Render (proceso largo)

## Funcionalidades

- Registro / login / logout (sesión persistente 30 días, rolling)
- Publicaciones con imagen
- Follow / unfollow + página explorar
- Likes y comentarios (AJAX)
- Notificaciones (like / comment / follow) con badge polling cada 30s
- Carga asincrónica del feed (infinite scroll)
- Landing pública con video de fondo

## Setup local

```bash
git clone https://github.com/IzaguirreCarlos/red_social_aficiones.git
cd red_social_aficiones

python -m venv venv
source venv/bin/activate          # WSL/Linux/macOS
# .\venv\Scripts\Activate.ps1     # Windows
pip install -r requirements.txt

cp .env.example .env              # luego edítalo

python manage.py migrate
python manage.py createsuperuser  # opcional
python manage.py runserver
```

Abre `http://127.0.0.1:8000/`.

## Deploy a Vercel

> Vercel corre Python como serverless functions. Por eso:
> - **No** se puede usar SQLite (filesystem efímero) → Postgres externo obligatorio.
> - **No** se puede subir imágenes al disco → Cloudinary obligatorio.

### 1) Provisiona los servicios externos

**Postgres** (gratis, escoge una):
- [Neon](https://neon.tech) — recomendado, instantáneo
- [Supabase](https://supabase.com)
- "Storage → Postgres" dentro del dashboard de Vercel

Copia el `DATABASE_URL` (formato `postgres://user:pass@host:5432/db?sslmode=require`).

**Cloudinary** (gratis):
1. Crea cuenta en [cloudinary.com](https://cloudinary.com)
2. Dashboard → copia `Cloud name`, `API Key`, `API Secret`

### 2) Aplica las migraciones a la Postgres remota

Una sola vez, desde tu máquina:

```bash
DATABASE_URL='postgres://...' python manage.py migrate
DATABASE_URL='postgres://...' python manage.py createsuperuser
```

### 3) Conecta el repo a Vercel

```bash
npm i -g vercel       # si no lo tienes
vercel login
vercel                # primer deploy interactivo
```

O desde la web: vercel.com → "New Project" → importa el repo de GitHub.

### 4) Configura las variables de entorno en Vercel

Dashboard del proyecto → Settings → Environment Variables:

| Variable | Valor |
|---|---|
| `SECRET_KEY` | un string largo aleatorio |
| `DATABASE_URL` | `postgres://...` (paso 1) |
| `CLOUDINARY_CLOUD_NAME` | de tu dashboard de Cloudinary |
| `CLOUDINARY_API_KEY` | id |
| `CLOUDINARY_API_SECRET` | id |
| `DJANGO_SETTINGS_MODULE` | `config.settings` |

`VERCEL` y `VERCEL_URL` los setea Vercel automáticamente — no los toques.

### 5) Redeploy

```bash
vercel --prod
```

`vercel.json` ya está configurado:
- `buildCommand` ejecuta `collectstatic` automáticamente
- `rewrites` envía todo a `api/index.py` (que carga el WSGI de Django)
- WhiteNoise sirve los estáticos a través del WSGI

## Deploy a Render (alternativa)

Tu proyecto también está listo para Render. `build.sh` y la detección `'RENDER' in os.environ` en `settings.py` están preparados:

1. New → Web Service → conecta el repo
2. Build command: `bash build.sh`
3. Start command: `gunicorn config.wsgi`
4. Setea `SECRET_KEY`, `DATABASE_URL`, `CLOUDINARY_*` igual que en Vercel
5. Add disk si quieres SQLite persistente (no recomendado, mejor Postgres)

## Estructura

```
config/         settings, urls, wsgi/asgi
accounts/       autenticación, Profile
posts/          Post, Comment, Like, Follow, Notification + signals
templates/      base, landing, includes
static/         css/styles.css (tema Claude), js/app.js
api/index.py    entrypoint Vercel (WSGI)
vercel.json     config Vercel
build.sh        config Render
runtime.txt     pin de versión de Python
```

## URLs principales

| Ruta | Descripción |
|---|---|
| `/` | Landing pública (video) |
| `/accounts/login/` · `/register/` | Auth con video |
| `/posts/` | Muro |
| `/posts/create/` | Publicar |
| `/posts/explore/` | Explorar usuarios |
| `/posts/notifications/` | Notificaciones |
| `/admin/` | Django admin |

## Troubleshooting Vercel

- **`DisallowedHost`** → la URL de tu deploy no está en `ALLOWED_HOSTS`. La detección `*.vercel.app` ya maneja esto. Si usas dominio custom, agrégalo en `ALLOWED_HOSTS` env var (separados por coma).
- **`CSRF verification failed`** → setea tu dominio custom en `CSRF_TRUSTED_ORIGINS` (vía env). Vercel `*.vercel.app` ya está cubierto.
- **`Error loading psycopg2`** → `pip install psycopg[binary]` y reemplaza `psycopg2-binary` en `requirements.txt`. Es más portable en serverless.
- **Cold start lento (~1-3s)** → es la naturaleza del serverless. Si te molesta, deploya en Render.
- **Las imágenes subidas no aparecen** → revisa que las 3 vars `CLOUDINARY_*` estén bien y que la cuenta de Cloudinary exista.
