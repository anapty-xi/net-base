import sys
sys.path.append('...')



from celery import shared_task
from config import celery


@shared_task
def create_table(table_name, cols, rows):
    connection = celery.DB_POOL.getconn()

    create_statement = f'''CREATE TABLE {table_name} ('''
    for col in cols:
        create_statement += f'''{col} text,'''

    rows = tuple([tuple(row.split(';')) for row in rows.split()])
    insert_statement = f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES"
    placeholders = ', '.join(['%s'] * len(cols))
    with connection.cursor() as cur:
        cur.execute(create_statement[:-1]+');')
        cur.executemany(insert_statement + f' ({placeholders})', rows)
        connection.commit()
    celery.DB_POOL.putconn(connection)
