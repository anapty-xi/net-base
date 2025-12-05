from ....config.pool import DB_ENGINE
from ..entities.table import Table as EntityTable
from sqlalchemy.schema import Table, Column
from ..usecases.table_gateway_protocol import TableGateway
from sqlalchemy.engine import Engine
from sqlalchemy import MetaData, String, insert
from typing import List

metadata_obj = MetaData()

class RepositoryManager(TableGateway):
    def __init__(self):
        self.engine = DB_ENGINE

    def create_table(self, table: EntityTable):
        columns = [Column(col, String) for col in table.cols]
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
        with self.engine.connect() as connection:
            connection.execute(insert(user_table), data)

    def get_table_info(self, title: str) -> List[List[str]]:
        if title:
            try:  
                table = [Table(title, metadata_obj, autoload_with=self.engine)]
                table_schema = [[table.name, table.columns] for table in table]
            except:
                raise Exception(f'Таблицы {table} не существует')
        else:
            metadata_obj.reflect(bind=self.engine)
        table_schema = [[table.name, [col.name for col in table.columns]] for table in metadata_obj.sorted_tables]
        return table_schema