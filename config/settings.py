"""
Django settings for config project.
Soporta deploy en Render y Vercel. SQLite sólo en dev local.
"""
from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

# ---------- Detección de entorno ----------
# Detecta producción por múltiples señales (no dependemos de una sola env var)
IS_VERCEL = bool(
    os.environ.get('VERCEL')
    or os.environ.get('VERCEL_ENV')
    or os.environ.get('VERCEL_URL')
    or os.environ.get('VERCEL_REGION')
    or os.path.exists('/var/task')        # filesystem del runtime de Vercel
)
IS_RENDER = bool(
    os.environ.get('RENDER')
    or os.environ.get('RENDER_EXTERNAL_HOSTNAME')
)
IS_PROD = IS_VERCEL or IS_RENDER
DEBUG = not IS_PROD

# ---------- ALLOWED_HOSTS ----------
ALLOWED_HOSTS = [h for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h]

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

VERCEL_URL = os.environ.get('VERCEL_URL')          # ej: my-app-abc123.vercel.app
if VERCEL_URL:
    ALLOWED_HOSTS.append(VERCEL_URL)

# En cualquier deploy de Vercel aceptamos todos los subdominios *.vercel.app
# y el alias .now.sh por compatibilidad.
if IS_VERCEL:
    ALLOWED_HOSTS += ['.vercel.app', '.now.sh']

# Last resort: si por alguna razón la detección falló pero estamos en prod
# con DATABASE_URL apuntando a un host remoto, permitimos cualquier host
# (es mejor que tirar 400 al usuario; las credenciales siguen protegidas).
if IS_PROD and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ['*']

# CSRF trusted origins (Django >= 4 exige esquema completo)
CSRF_TRUSTED_ORIGINS = []
if VERCEL_URL:
    CSRF_TRUSTED_ORIGINS.append(f'https://{VERCEL_URL}')
if IS_VERCEL:
    CSRF_TRUSTED_ORIGINS.append('https://*.vercel.app')
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')

if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# ---------- Apps ----------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'cloudinary_storage',
    'django.contrib.staticfiles',

    'cloudinary',
    'accounts',
    'posts',
]

# ---------- Cloudinary (media en producción) ----------
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY':    os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}

# ---------- Middleware ----------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ---------- Base de datos ----------
# En producción se EXIGE DATABASE_URL apuntando a Postgres.
# SQLite no es viable en serverless (filesystem efímero/read-only).
DATABASE_URL = os.environ.get('DATABASE_URL')
if IS_PROD and not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL es obligatorio en producción. Crea una Postgres "
        "(Neon, Supabase, Vercel Postgres, Render Postgres) y expórtala."
    )

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        ssl_require=IS_PROD,
    )
}

# ---------- Validadores de password ----------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------- Seguridad en prod ----------
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ---------- Sesiones (persistentes 30 días) ----------
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_PATH = '/'
SESSION_COOKIE_SAMESITE = 'Lax'

# ---------- I18N ----------
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ---------- Static files ----------
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ---------- Auth redirects ----------
LOGIN_URL = '/accounts/login/'
LOGOUT_REDIRECT_URL = '/'
