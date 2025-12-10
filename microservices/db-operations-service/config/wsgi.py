'''
Конфигурирование сервера для создания и закрытия пула подключений при инициализации и закрытии
'''
import os
import django
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
from . import pool
pool.create_db_engine()


django.setup()
application = get_wsgi_application()


import atexit
import signal

def shutdown():
    pool.shutdown_engine()

atexit.register(shutdown)


signal.signal(signal.SIGTERM, lambda sig, frame: shutdown())
signal.signal(signal.SIGINT, lambda sig, frame: shutdown())  
