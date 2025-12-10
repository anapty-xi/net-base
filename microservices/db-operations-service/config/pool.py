'''
модуль для определения операций выполняющихся при запуске и отключении сервера
'''

import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv


load_dotenv()

DB_ENGINE: Engine | None = None

def create_db_engine() -> None:
    '''
    Создание пула подключений с помощью sqlalchemy engine, который используется в инфраструктуре
    '''
    global DB_ENGINE
    try:
        DB_ENGINE = create_engine(
            str(os.getenv('DB_URL')),
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False,  
            )
        print('пул готов')


    except Exception as e:
        print(f'ошибка {e}')

def shutdown_engine():
    '''
    Закрытие пула подключений и замена значения переменной на None
    '''
    global DB_ENGINE
    if DB_ENGINE:
        DB_ENGINE.dispose()
        DB_ENGINE = None
        print('подключение закрыто')
