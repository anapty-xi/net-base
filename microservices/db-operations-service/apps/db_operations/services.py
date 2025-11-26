import requests
import logging

from config import pool
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile

logger = logging.getLogger(__name__)

class CsvHandler:
    '''класс предосталяющий части таблицы для ее создания'''
    def __init__(self, file: UploadedFile):
        if not file.name.endswith('.csv'):
            raise TypeError
        self.file = file
    def table_title(self):
        return self.file.name.endswith('.csv')
    def cols(self):
        return self.file.file.readline().decode('utf-8-sig').strip().split(';')
    def rows(self):
        return self.file.file.read().decode('utf-8')



def get_tables_with_cols(table=None):  # TODO: подумать над сохранением состояния
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
        try:
            cur.execute(query)
            result = cur.fetchall()
        except Exception as e:
            logger.error(f'ошибка запроса {e}')
            return None
        finally:
            pool.DB_POOL.putconn(connection)
        json_res = {}
        for table, col in result:
            if table in json_res.keys():
                json_res[table].append(col)
            else:
                json_res[table]=[col]
        return json_res
        
    
    
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


def get_user_from_token(token):
    try:
        header = {'Authorization': f'Bearer {token}'}
        response = requests.get(
            f'{settings.USER_SERVICE_URL}/user/user/',
            headers=header,
            timeout=15
        )
        if response.status_code == 200:
            return response.json()
        return None
    except: return None