web: gunicorn --env DJANGO_SETTINGS_MODULE=config.settings.production --chdir ./app config.wsgi:application --bind 0.0.0.0:$PORT