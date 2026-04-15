#!/bin/sh

set -e  # exit on error

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "loading fixture data"
python manage.py loaddata events.json

echo "Starting server..."
gunicorn --bind 0.0.0.0:8000 --workers 3 config.wsgi:application