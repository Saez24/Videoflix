#!/bin/sh

set -e

echo "Wait for PostgreSQL at $DB_HOST:$DB_PORT..."

# Check if the required environment variables are set
while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -q; do
  echo "PostgreSQL is not ready yet - sleepping for 1 second..."
  sleep 1
done

echo "PostgreSQL is ready!"

# SECRET_KEY generation if not set
if [ -z "$SECRET_KEY" ]; then
  echo "Generating new SECRET_KEY..."
  export SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
  echo "New SECRET_KEY generated"
fi

python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate

# Create a superuser using environment variables
python manage.py shell <<EOF
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'adminpassword')

if not User.objects.filter(username=username).exists():
    print(f"Creating superuser '{username}'...")
    # Korrekter Aufruf: username hier übergeben
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created.")
else:
    print(f"Superuser '{username}' already exists.")
EOF

python manage.py rqworker default &

exec gunicorn videoflix.wsgi:application --bind 0.0.0.0:8000
