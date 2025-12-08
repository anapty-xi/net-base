from config.pool import DB_ENGINE
from ..entities.table import Table as EntityTable
from sqlalchemy.schema import Table, Column
from ..usecases.table_gateway_protocol import TableGateway
from sqlalchemy.engine import Engine
from sqlalchemy import MetaData, String, insert, update, select, Integer
from typing import List, Dict

metadata_obj = MetaData()

class RepositoryManager(TableGateway):
    def __init__(self):
        self.engine: Engine = DB_ENGINE

    def _get_table_obj(self, title: str) -> Table:
        try:  
            return Table(title, metadata_obj, autoload_with=self.engine)
        except:
            raise Exception(f'Таблицы {title} не существует')

    def create_table(self, table: EntityTable) -> bool:
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
        return True #TODO возвращять значание взависимости от создания таблицы

    def get_table_info(self, title: str) -> Dict[str, List[str]]:
        if title:
            table = self._get_table_obj(title)
            table_schema = {table.name: [col.name for col in table.columns]}
        else:
            metadata_obj.reflect(bind=self.engine)
            table_schema = {table.name: [col.name for col in table.columns] for table in metadata_obj.sorted_tables}
        return table_schema
    
    def update_row(self, title: str, row_id: str, updates: Dict[str, str]) -> bool:
        table = self._get_table_obj(title)
        table_cols = [col.name for col in table.columns]
        for col in updates:
            if col not in table_cols:
                raise ValueError(f'Столбец {col} не является столбцом таблицы {title}')
        stmt = update(table).where(table.c.id == int(row_id)).values(**updates)
        with self.engine.begin() as connection:
            connection.execute(stmt)
        return True
    
    def delete_table(self, title: str) -> bool:
        table = self._get_table_obj(title)
        table.drop(self.engine)
        if title in metadata_obj.tables:
            metadata_obj.remove(table)
        return True

    def get_rows(self, title: str, query_params: Dict[str, str]) -> List[List[str]]:
        table = self._get_table_obj(title)
        table_cols = [col.name for col in table.columns]
        for col in query_params:
            if col not in table_cols:
                raise ValueError(f'Столбец {col} не является столбцом таблицы {title}')
        stmt = select(table)
        for col, val in query_params.items():
            stmt = stmt.where(table.columns[col] == val)
        with self.engine.connect() as connection:
            result = connection.execute(stmt)
        rows = result.fetchall()
        return [list(row) for row in rows]
