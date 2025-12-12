from apps.analytics.infrastructure.reporter import Reporter
from apps.analytics.entities.table_report import TableReport


class TestReporter:
    def test_get_table_report(self, table_report):
        reporter = Reporter()
        result_report = reporter.get_table_report('test', ['id', 'проверено', 'дата', 'примечание'],
                                                  [
                                                      [1, '+', '12.12.2025', ''],
                                                      [2, '+', '12.12.2025', ''],
                                                      [3, 'з', '12.12.2025', ''],
                                                      [4, 'з', '12.12.2025', ''],
                                                      [5, 'у', '12.12.2025', ''],
                                                      [6, '+', '11.12.2025', ''],
                                                      [7, 'з', '11.12.2025', ''],
                                                      [8, 'у', '11.12.2025', ''],
                                                      [9, '', '', '']
                                                  ])

        assert result_report == table_report