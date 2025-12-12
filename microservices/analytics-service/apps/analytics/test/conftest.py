from sys import path
import pytest


path.insert(0, '/home/anapty-xi/Документы/projects/net-base/microservices/analytics-service/')

from apps.analytics.entities.table_report import TableReport

@pytest.fixture
def table_report():
    return TableReport(
        title='test',
        all_rows=9,
        checked=8,
        success=5,
        remarks=3,
        elemenated_remarks_today=1,
        checked_today=5,
        remarks_today=2,
        rest=1
    )