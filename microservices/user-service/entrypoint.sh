#!/bin/sh

mkdir -p /var/html/static

python manage.py migrate --noinput
python manage.py collectstatic --noinput

python admin.py

exec "$@"