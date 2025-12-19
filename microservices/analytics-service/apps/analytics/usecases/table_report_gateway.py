from typing import Protocol
from typing import Self, List, Dict
from ..entities.table_report import TableReport 
from datetime import datetime

class TableReportProtocol(Protocol):
    def get_table_report(self, table_title: str, table_cols: List[str], table_rows: List[List[str]]) -> TableReport:
        ...
    def get_analytics_schemes(self) -> Dict[str, List[str]]:
        ...
    def get_table_rows(self, table_title) -> List[List[str]]:
        ...
    def report_for_date(self, date: datetime.date) -> List[TableReport]:
        ...