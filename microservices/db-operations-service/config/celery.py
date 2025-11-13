import os
from psycopg2.pool import ThreadedConnectionPool
from celery import Celery
from celery.signals import worker_process_init, worker_process_shutdown


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

DB_POOL = None


try:
    DB_POOL = ThreadedConnectionPool(5, 10, host='127.0.0.1',
                                 port=5432,
                                 user='postgres',
                                 database='users',
                                 password='1247')
    print('пул готов')
except Exception as e:
    print('ошибка пула')
    DB_POOL = None


@worker_process_shutdown.connect
def shutdown_pool(**kwargs):
    global DB_POOL
    if DB_POOL:
        DB_POOL.closeall()
        DB_POOL = None
        print('подключение закрыто')