import logging

from .table_report_gateway import TableReportProtocol
from ..entities.table_report import TableReport
from typing import List

logger = logging.getLogger(__name__)

class MakeReport:
    '''
    Создание отчета
    '''
    def __init__(self, reporter: TableReportProtocol):
        self.reporter = reporter

    def execute(self) -> List[TableReport]:
        tabels_to_report = self.reporter.get_analytics_schemes()
        logger.info(f'tables for report {tabels_to_report}')
        report = []
        for table_title, cols in tabels_to_report.items():
            table_rows = self.reporter.get_table_rows(table_title)

            report.append(self.reporter.get_table_report(table_title, 
                                                         cols,
                                                         table_rows))
        return report
