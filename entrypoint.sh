#!/bin/sh

set -e  # exit on error

if [ "${RUN_MIGRATIONS_ON_STARTUP:-0}" = "1" ]; then
	echo "Applying database migrations..."
	python manage.py migrate --noinput
fi

if [ "${LOAD_FIXTURES_ON_STARTUP:-0}" = "1" ]; then
	echo "Loading fixture data..."
	python manage.py loaddata events.json
fi

echo "Starting server..."
exec gunicorn config.wsgi --log-file -
