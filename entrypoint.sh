#!/bin/sh

set -e  # exit on error

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "loading fixture data"
python manage.py loaddata events.json

echo "Starting server..."
exec gunicorn config.wsgi --log-file -