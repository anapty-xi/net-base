'''модуль для определения операций выполняющихся при запуске и отключении Uvicorn'''

import psycopg2

CONNECTION = None

def create_db_connection():
    global CONNECTION
    try:
        CONNECTION = psycopg2.connect(host='127.0.0.1',
                                 port=5432,
                                 user='postgres',
                                 database='users',
                                 password='1247')
        print('подключение готово')


    except Exception as e:
        print(f'ошибка {e}')

def shutdown_connection():
    global CONNECTION
    if CONNECTION:
        CONNECTION.close()
        CONNECTION = None
        print('подключение закрыто')
