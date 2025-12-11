from .table_report_gateway import TableReportProtocol
from ..entities.table_report import TableReport
from typing import List

class MakeReport:
    '''
    Создание отчета
    '''
    def __init__(self, reporter: TableReportProtocol):
        self.reporter = reporter

    def execute(self, table_title, cols) -> List[TableReport]:
        rows_number = self.reporter.get_rows_number()
        checked = self.reporter.get_cheked_number()
        success = self.reporter.get_success_number()
        remarks = self.reporter.get_remarks_number()
        elem_remarks_td = self.reporter.get_elem_remarks_td_number()
        remarks_td = self.reporter.get_remarks_td_number()
        cheked_today = self.reporter.get_cheked_number()
        rest = rows_number - checked
        table_report = TableReport(
            title=table_title,
            all_rows=rows_number,
            cheked=checked,
            success=success,
            remarks=remarks,
            elemenated_remarks_today=elem_remarks_td,
            remarks_today=remarks_td,
            cheked_today=cheked_today,
            rest=rest
        )
        return table_report

