'''модуль для определения операций выполняющихся при запуске и отключении Uvicorn'''

from psycopg2.pool import ThreadedConnectionPool

DB_POOL = None

def create_db_pool():
    global DB_POOL
    try:
        DB_POOL = ThreadedConnectionPool(5, 10, host='127.0.0.1',
                                 port=5432,
                                 user='postgres',
                                 database='users',
                                 password='1247')
        print('пул готов')


    except Exception as e:
        print(f'ошибка {e}')

def shutdown_pool():
    global DB_POOL
    if DB_POOL:
        #DB_POOL.closeall()
        DB_POOL = None
        print('подключение закрыто')
