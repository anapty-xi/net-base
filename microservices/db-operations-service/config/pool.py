import asyncpg
from .settings import DB_POOL

async def create_db_pool():
    try:
        await asyncpg.create_pool(host='127.0.0.1',
                                 port=5432,
                                 user='postgres',
                                 database='users',
                                 password='1247')
        print('пул готов')

    except Exception as e:
        print(f'ошибка {e}')

async def shutdown_pool():
    if DB_POOL:
        await DB_POOL.close()
        DB_POOL = None
        print('пул закрыт')
