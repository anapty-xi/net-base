from ....config.pool import DB_ENGINE
from ..entities.table import Table as EntityTable
from sqlalchemy.schema import Table as SQLAlchemyTable
from ..usecases.table_gateway_protocol import TableGateway
from sqlalchemy.engine import Engine

class RepositoryManager(TableGateway):
    def __init__(self, engine: Engine):
        self.engine = engine

    def create_table(self, table: EntityTable):
        with self.engine.connect() as connection:
            pass