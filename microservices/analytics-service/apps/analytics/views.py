import json
import logging
import datetime

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .usecases.table_report_usecases import MakeReport
from .infrastructure.reporter import Reporter
from rest_framework import status
from .permissions import IsAuthenticated

logger = logging.getLogger(__name__)


@api_view(['GET'])    
@permission_classes([IsAuthenticated])
def get_report(request):                             
    '''
    Точка только для аутентифицированнных пользователей для получения отчета о таблицах
    '''
    date = request.GET.get('date')
    logger.info(f'date = {date}')
    if not date:
        return Response(
            {'error': 'no date'},
            status=status.HTTP_400_BAD_REQUEST
        )
    day, month, year = date.split('.')
    date = datetime.date(int(year), int(month), int(day))

    reporter = Reporter()
    usecase = MakeReport(reporter)
    try:
        report = usecase.execute(date)
        logger.info(f'reports {len(report)}')
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    if report:
        return Response(
            [json.loads(table_report.json()) for table_report in report],
            status=status.HTTP_200_OK
        )
    logger.info('нет репортов на эту дату')
    return Response(
        {'error': 'no reports'},
        status=status.HTTP_404_NOT_FOUND
    )

