import json

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .usecases.table_report_usecases import MakeReport
from .infrastructure.reporter import Reporter
from rest_framework import status
from .permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_report(request):
    '''
    Точка только для аутентифицированнных пользователей для получения отчета о таблицах
    '''
    reporter = Reporter()
    usecase = MakeReport(reporter)
    try:
        report = usecase.execute()
    except Exception as e:
        return Response(
            {'error': e},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    return Response(
        [json.loads(table_report) for table_report in report],
        status=status.HTTP_200_OK
    )

