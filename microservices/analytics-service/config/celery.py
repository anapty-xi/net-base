'''
настройка celery, словарь с запланированными тасками
'''
import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'save_report': {
        'task': 'apps.analytics.tasks.save_report',
        'schedule': crontab(hour=23, minute=59)
    }
}