from celery import shared_task
import psycopg2

@shared_task
def create_table(table_name, cols):
    connection = psycopg2.connect(host='127.0.0.1',
                            port=5432,
                            user='postgres',
                            database='users',
                            password='1247')
    
    cur = connection.cursor()
    statement = f'''CREATE TABLE {table_name} ('''
    for col in cols:
        statement += f'''{col} text,'''

    cur.execute(statement[:-1]+');')
    connection.commit()
    connection.close()
