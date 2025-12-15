from ..entities.table import Table
from typing import Optional, List, Dict
from .table_gateway_protocol import TableGateway
from .table_validator import TableValidator, UpdatesValidator


class UseCase:
    def __init__(self, infrastructure_class: TableGateway):
        self.infrastructure_class = infrastructure_class

class CreateTable(UseCase):
    def execute(self, title: str, cols: List[str], rows: List[List[str]], in_analytics: bool):
        table = Table(
            title=title,
            cols=cols,
            rows=rows,
            in_analytics=in_analytics
        )
        validator = TableValidator()
        validated_table = validator.validate_table(table)
        return self.infrastructure_class.create_table(validated_table)
    
class TableInfo(UseCase):
    def execute(self, title=None):
        tables_data = self.infrastructure_class.get_table_info(title)
        return tables_data
    
class UpdateTable(UseCase):
    def execute(self, title: str, row_id: str, updates: Dict[str, str]):
        table_schema = self.infrastructure_class.get_table_info(title)
        validator = UpdatesValidator()
        validated_updates = validator.cheked_field_validation(table_schema[title], **updates)
        return self.infrastructure_class.update_row(title, row_id, validated_updates)
    
class DeleteTable(UseCase):
    def execute(self, title: str):
        return self.infrastructure_class.delete_table(title)
    
class GetRows(UseCase):
    def execute(self, title: str, query_params: Dict[str, str]):
        return self.infrastructure_class.get_rows(title, query_params)