web: bash ./start.sh
release: cd backend && python manage.py migrate
web: cd backend && gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app.wsgi:application