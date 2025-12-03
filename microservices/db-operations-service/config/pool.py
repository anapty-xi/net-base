'''модуль для определения операций выполняющихся при запуске и отключении Uvicorn'''

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool

DB_ENGINE: Engine | None = None

def create_db_engine() -> None:
    global DB_ENGINE
    try:
        DB_ENGINE = create_engine(
            "postgresql+psycopg2://postgres:1247@127.0.0.1:5432/users",
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
    global DB_ENGINE
    if DB_ENGINE:
        DB_ENGINE.dispose()
        DB_ENGINE = None
        print('подключение закрыто')
