from config.pool import DB_ENGINE
from ..entities.table import Table as EntityTable
from sqlalchemy.schema import Table, Column
from ..usecases.table_gateway_protocol import TableGateway
from sqlalchemy.engine import Engine
from sqlalchemy import MetaData, String, insert, update, select, Integer
from typing import List, Dict

metadata_obj = MetaData()

class RepositoryManager(TableGateway):
    '''
    Шлюз к бд на sqlalchemy. Отвечает протоколу TableGateway
    '''
    def __init__(self, engine=None):
        if engine:
            self.engine = engine
        else: self.engine: Engine = DB_ENGINE

    def _get_table_obj(self, title: str) -> Table:
        try:  
            return Table(title, metadata_obj, autoload_with=self.engine)
        except:
            raise Exception(f'Таблицы {title} не существует')

    def create_table(self, table: EntityTable) -> bool:
        '''
        Создвние таблицы и заполнение ее данными
        '''
        try:
            columns = [Column(col, String, nullable=True) for col in table.cols]
            columns.insert(0, Column('id', Integer, primary_key=True, autoincrement=True))
            user_table = Table(
                table.title,
                metadata_obj,
                *columns
            )
            metadata_obj.create_all(self.engine)

            data = [
                {col: row[i] for i, col in enumerate(table.cols)}
                for row in table.rows
            ]
            with self.engine.begin() as connection:
                connection.execute(insert(user_table), data)
            return True
        except:
            return False



    def get_table_info(self, title: str) -> Dict[str, List[str]]:
        '''
        Получение схемы всех таблиц или конкретной таблицы 
        '''
        if title:
            table = self._get_table_obj(title)
            table_schema = {table.name: [col.name for col in table.columns]}
        else:
            metadata_obj.reflect(bind=self.engine)
            table_schema = {table.name: [col.name for col in table.columns] for table in metadata_obj.sorted_tables}
        return table_schema
    
    def update_row(self, title: str, row_id: str, updates: Dict[str, str]) -> bool:
        '''
        Обновление значений определенной строки в таблице 
        '''
        table = self._get_table_obj(title)
        table_cols = [col.name for col in table.columns]
        for col in updates:
            if col not in table_cols:
                raise ValueError(f'Столбец {col} не является столбцом таблицы {title}')
        stmt = update(table).where(table.c.id == int(row_id)).values(**updates)
        with self.engine.begin() as connection:
            try:
                connection.execute(stmt)
                return True
            except:
                return False
    
    def delete_table(self, title: str) -> bool:
        '''
        Удаление таблицы
        '''
        table = self._get_table_obj(title)
        table.drop(self.engine)
        if title in metadata_obj.tables:
            metadata_obj.remove(table)
        return True

    def get_rows(self, title: str, query_params: Dict[str, str]) -> List[List[str]]: 
        '''
        Получения всех строк удвлотворяющих параментрам поиска
        '''
        table = self._get_table_obj(title)
        table_cols = [col.name for col in table.columns]
        stmt = select(table)
        if query_params:
            for col in query_params:
                if col not in table_cols:
                    raise ValueError(f'Столбец {col} не является столбцом таблицы {title}')            
            for col, val in query_params.items():
                stmt = stmt.where(table.columns[col] == val)
        with self.engine.connect() as connection:
            result = connection.execute(stmt)
        rows = result.fetchall()
        return [list(row) for row in rows]
