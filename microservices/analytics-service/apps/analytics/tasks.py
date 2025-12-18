from config.celery import app
from .usecases.table_report_usecases import MakeReport
from .infrastructure.reporter import Reporter
from .models import Report

@app.task
def save_report():
    reporter = Reporter()
    usecase = MakeReport(reporter)
    reports = usecase.execute()
    for entity_report in reports:
        report_for_save = Report.objects.create(
            title = entity_report.title,
            all_rows = entity_report.all_rows,
            checked = entity_report.checked,
            success = entity_report.success,
            remarks = entity_report.remarks,
            elemenated_remarks_today = entity_report.elemenated_remarks_today,
            remarks_today = entity_report.remarks_today,
            checked_today = entity_report.checked_today,
            rest = entity_report.rest,
        )
        report_for_save.save()