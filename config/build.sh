#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py shell -c "from game.seed import load; load()"
python manage.py shell -c "from game.langs import load; load()"
python manage.py createsuperuser --no-input || true