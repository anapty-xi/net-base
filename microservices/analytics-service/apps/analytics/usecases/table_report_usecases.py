from .table_report_gateway import TableReportProtocol
from ..entities.table_report import TableReport

class MakeReport:
    def __init__(self, reporter: TableReportProtocol):
        self.reporter = reporter

    def execute(self, table_title: str) -> TableReport | Exception:
        rows_number = self.reporter.get_rows_number(table_title)
        checked = self.reporter.get_cheked_number(table_title)
        success = self.reporter.get_success_number(table_title)
        remarks = self.reporter.get_remarks_number(table_title)
        elem_remarks_td = self.reporter.get_elem_remarks_td_number(table_title)
        remarks_td = self.reporter.get_remarks_td_number(table_title)
        cheked_today = self.reporter.get_cheked_number(table_title)
        rest = rows_number - checked
        report = TableReport(
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
        return report
