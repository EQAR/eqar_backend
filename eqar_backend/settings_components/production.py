import os

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
from eqar_backend.settings import BASE_DIR

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['.herokuapp.com']

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'public')

MEDIA_URL = '/reports/'

CORS_ORIGIN_ALLOW_ALL = True

# CELERY STUFF
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Brussels'

# Meilisearch
MEILI_API_URL = "http://localhost:7700"

USE_TZ = False

DJOSER = {
    'SERIALIZERS': {
        'current_user': 'accounts.serializers.CurrentUserSerializer',
    },
}

# Connect API: time for which issued VCs may be cached
VC_CACHE_MAX_AGE = 86400
