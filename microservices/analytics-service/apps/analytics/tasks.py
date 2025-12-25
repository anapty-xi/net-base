import logging


from config.celery import app
from .usecases.table_report_usecases import MakeReport
from .infrastructure.reporter import Reporter
from .models import Report

logger = logging.getLogger(__name__)

@app.task(queue='analytics')
def save_report():
    reporter = Reporter()
    usecase = MakeReport(reporter)
    reports = usecase.execute(None)
    if reports:
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
            logger.info(f'репорт для таблицы {entity_report.title} сохранен')
    else:
        logger.info('ни одного репорта не было сохранено')