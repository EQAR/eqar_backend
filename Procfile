release: python manage.py migrate
web: gunicorn eqar_backend.wsgi --log-file -
mcp: python manage.py runmcp --port $PORT
