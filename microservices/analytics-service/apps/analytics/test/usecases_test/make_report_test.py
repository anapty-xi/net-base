from unittest.mock import Mock, patch
from apps.analytics.usecases.table_report_usecases import MakeReport
from apps.analytics.infrastructure.reporter import Reporter
from apps.analytics.entities.table_report import TableReport


class TestMakeReport:
    def test_make_report(self, table_report):
        class FakeTableReporter(Reporter):
            def get_analytics_schemes(self):
                return {
                    "test": ["ID", "Проверено", "Дата"],
                    "table2": ["ID", "Проверено", "Дата"],
                }

            def get_table_rows(self, table_title):
                if table_title == "test":
                    return [
                        [1, '+', '12.12.2025', ''],
                        [2, '+', '12.12.2025', ''],
                        [3, 'з', '12.12.2025', ''],
                        [4, 'з', '12.12.2025', ''],
                        [5, 'у', '12.12.2025', ''],
                        [6, '+', '11.12.2025', ''],
                        [7, 'з', '11.12.2025', ''],
                        [8, 'у', '11.12.2025', ''],
                        [9, '', '', '']
                    ]
                elif table_title == 'table2':
                    return [
                        [1, '+', '12.12.2025', ''],
                        [2, '+', '11.12.2025', ''],
                        [3, 'з', '11.12.2025', ''],
                        [4, 'з', '11.12.2025', ''],
                    ]
        report = MakeReport(FakeTableReporter()).execute()
        assert report == [table_report, TableReport(
            title='table2',
            all_rows=4,
            checked=4,
            success=2,
            remarks=2,
            elemenated_remarks_today=0,
            remarks_today=0,
            checked_today=1,
            rest=0
        )]