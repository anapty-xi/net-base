import sys
sys.path.append('...')



from celery import shared_task
from config import celery


@shared_task
def create_table(table_name, cols):
    connection = celery.DB_POOL.getconn()
    
    cur = connection.cursor()
    statement = f'''CREATE TABLE {table_name} ('''
    for col in cols:
        statement += f'''{col} text,'''

    cur.execute(statement[:-1]+');')
    connection.commit()
    celery.DB_POOL.putconn(connection)
