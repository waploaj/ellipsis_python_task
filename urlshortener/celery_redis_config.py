from celery.schedules import crontab
from decouple import config

REDIS_HOST = 'localhost'
REDIS_PORT = '6379'
REDIS_DB = 0
BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'

BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'

CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = config('TIME_ZONE')
CELERY_ENABLE_UTC = True

CELERY_BEAT_SCHEDULE = {
    'check-expired-urls-to-notify-owners': {
        'task': 'shortener_platform.tasks.check_expired_urls',
        'schedule': crontab(minute='*/5'),
    },
}
