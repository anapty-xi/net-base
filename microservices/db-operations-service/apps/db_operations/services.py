import psycopg2
from config import pool

def get_tables_with_cols():
    connection = pool.DB_POOL.getconn()
    with connection.cursor() as cur:
        query = '''SELECT
                    table_name,
                    column_name,
                    data_type
                FROM
                    information_schema.columns
                WHERE
                    table_schema = 'public'
                ORDER BY
                    table_name,
                    ordinal_position;
                '''
        cur.execute(query)
        pool.DB_POOL.putconn(connection)
        return cur.fetchall()
    
    
def delete_table(table):
    connection = pool.DB_POOL.getconn()
    with connection.cursor() as cur:
        query = f'''DROP TABLE {table}'''
        try:
            cur.execute(query)
            connection.commit()
            return True
        except:
            return False
        finally: pool.DB_POOL.putconn(connection)
