import psycopg2
from config import pool

def get_tables_with_cols(table=None):
    connection = pool.DB_POOL.getconn()
    with connection.cursor() as cur:
        if table:
            query = f'''SELECT
                        column_name
                    FROM
                        information_schema.columns
                    WHERE
                        table_name = '{table}'
                        AND table_schema = 'public'
                    ORDER BY
                        ordinal_position;
                    '''
        else:
            query = '''SELECT
                        table_name,
                        column_name
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


def get_rows(table, **kwagrs):
    query = f'''SELECT * FROM {table}
                WHERE '''
    where_part = ' AND '.join([f"{key} = '{val}'" for key, val in kwagrs.items()])
    connection = pool.DB_POOL.getconn()
    with connection.cursor() as cur:
        try:
            cur.execute(query+where_part)
            return cur.fetchall()
        except: 
            return None
        finally: pool.DB_POOL.putconn(connection)


def update_row(table, pk, **kwargs):
    query = f'''UPDATE {table} SET '''
    for col, value in kwargs.items():
        query += f"{col} = '{value}', "
    query = query[:-2] + f' WHERE {table}_id = {pk}'
    connection = pool.DB_POOL.getconn()
    with connection.cursor() as cur:
        try:
            cur.execute(query)
            connection.commit()
            return True
        except: 
            return None
        finally: pool.DB_POOL.putconn(connection)