import os
from celery import Celery
from celery.signals import worker_process_init, worker_process_shutdown
from config import pool

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@worker_process_init.connect
def init_db_pool(**kwargs):
    pool.create_db_pool()
    print('пул готов')

@worker_process_shutdown.connect
def shutdown_pool(**kwargs):
    pool.shutdown_pool()
    print('пул готов')