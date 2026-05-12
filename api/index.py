"""Entrypoint serverless de Vercel.

Vercel detecta este archivo dentro de /api y lo ejecuta como una función
Python. Exponemos la aplicación WSGI de Django en la variable `app`,
que es la convención que espera el runtime de Python de Vercel.
"""
import os
import sys

# Aseguramos que la raíz del proyecto está en sys.path para encontrar `config`
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from config.wsgi import application as app  # noqa: E402

# Compatibilidad con runtimes que esperan `handler` en lugar de `app`
handler = app
