#!/bin/bash
# Lee el archivo .env y sube cada variable a Vercel (production + preview + development)
set -e

VERCEL="/home/alberto24/.local/node_modules/.bin/vercel"
ENV_FILE=".env"

if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: No se encontró el archivo .env"
  echo "Copia .env.example a .env y rellena los valores reales."
  exit 1
fi

VARS=("SECRET_KEY" "DATABASE_URL" "CLOUDINARY_CLOUD_NAME" "CLOUDINARY_API_KEY" "CLOUDINARY_API_SECRET")

for VAR in "${VARS[@]}"; do
  VALUE=$(grep "^${VAR}=" "$ENV_FILE" | cut -d '=' -f2-)
  if [ -z "$VALUE" ]; then
    echo "AVISO: $VAR no encontrado en .env, se omite."
    continue
  fi
  echo "Subiendo $VAR..."
  for ENV in production preview development; do
    echo "$VALUE" | "$VERCEL" env add "$VAR" "$ENV" --force 2>/dev/null || \
    echo "$VALUE" | "$VERCEL" env add "$VAR" "$ENV"
  done
done

echo ""
echo "Listo. Variables subidas a Vercel."
