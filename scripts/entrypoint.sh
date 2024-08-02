
#!/usr/bin/env bash

set -e


RUN_MANAGE_PY='poetry run python manage.py'

# Start Celery worker in the background
$poetry run celery -A core worker --loglevel=info

exec poetry run python3 manage.py runserver