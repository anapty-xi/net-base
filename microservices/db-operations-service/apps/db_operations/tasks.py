import sys
sys.path.append('...')



from celery import shared_task
from config import pool

@shared_task
def create_pool():
    pool.create_db_pool()

create_pool.delay()

@shared_task
def create_table(table_name, cols):
    from config import pool
    connection = pool.DB_POOL.getconn()
    
    cur = connection.cursor()
    statement = f'''CREATE TABLE {table_name} ('''
    for col in cols:
        statement += f'''{col} text,'''

    cur.execute(statement[:-1]+');')
    connection.commit()
    pool.DB_POOL.putconn()
