python manage.py collectstatic --noinput
python manage.py migrate --noinput
gunicorn hrms_project.wsgi --bind 0.0.0.0:$PORT