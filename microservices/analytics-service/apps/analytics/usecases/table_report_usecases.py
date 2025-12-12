from .table_report_gateway import TableReportProtocol
from ..entities.table_report import TableReport
from typing import List

class MakeReport:
    '''
    Создание отчета
    '''
    def __init__(self, reporter: TableReportProtocol):
        self.reporter = reporter
    
    def execute(self) -> List[TableReport]:
        tabels_to_report = self.reporter.get_analytics_schemes()
        report = []
        for table_title, cols in tabels_to_report.items():
            table_rows = self.reporter.get_table_rows(table_title)
            report.append(self.reporter.get_table_report(table_title, 
                                                         cols,
                                                         table_rows))
        return report
