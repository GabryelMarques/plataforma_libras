#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Cria o SEU usuário admin automaticamente se não existir
python manage.py createsuperuser --noinput --username gabryel --email gabryelmarques17@gmail.com || true