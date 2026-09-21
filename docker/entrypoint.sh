#!/bin/sh
# Lancé à chaque démarrage du conteneur web, avant gunicorn.
# Un seul conteneur web existe : pas de risque de migrations concurrentes.
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
