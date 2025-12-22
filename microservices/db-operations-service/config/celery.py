import os
from celery import Celery
from celery.beat import crontab
from celery.signals import worker_process_init, worker_process_shutdown
from . import pool


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()



@worker_process_init.connect
def init_worker(**kwargs):
    pool.create_db_engine()



@worker_process_shutdown.connect
def shutdown_pool(**kwargs):
    print('hi')
    pool.shutdown_engine()


app.conf.beat_schedule = {
    'db_dump': {
        'task': 'apps.db_operations.tasks.db_dump',
        'schedule': 30.0#crontab(hour=23, minute=59)
    }
}