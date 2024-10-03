#!/usr/bin/env bash
# exit on error
set -o errexit
echo "Running migrations, creating super user, and collecting static"
echo "RENDER_EXTERNAL_HOSTNAME is set to $RENDER_EXTERNAL_HOSTNAME";
echo "RENDER_EXTERNAL_URL is set to $RENDER_EXTERNAL_URL";
python manage.py migrate
python manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL || echo "Superuser already exists"
echo "Ready for app server"
gunicorn core.wsgi:application --bind 0.0.0.0:$PORT