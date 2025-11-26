import logging

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import SerializerQueryConditions, SerializerColUpdate
from . import tasks
from . import services
from .permissions import IsAdminCustom,IsAuthenticatedCustom

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAdminCustom])
@parser_classes([MultiPartParser, FormParser])
def create_table(request):
    '''создание и заполнение таблицы по переданному csv файлу'''

    if 'file' not in request.data:
        return Response(
            {'error': 'csv файл необходим'},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        file = services.CsvHandler(request.data['file'])
    except TypeError:
        return Response(
            {'error': 'файл должен быть csv'},
            status=status.HTTP_400_BAD_REQUEST
        )
    tasks.create_table.delay(file.table_title, file.cols, file.rows)
    return Response (
        status=status.HTTP_201_CREATED
    )

@api_view(['GET'])
@permission_classes([IsAuthenticatedCustom])
def get_all_tabels(request):
    '''получание всех таблиц и их столбцов'''

    result = services.get_tables_with_cols()
    if not result:
        return Response(
            {'error': 'ошибка запроса к бд'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    return Response(
        {'tabels': result},
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([IsAuthenticatedCustom])
def get_table(request, table):
    '''получание столбов конкретной таблицы'''

    result = services.get_tables_with_cols(table)
    if not result:
        return Response(
            {'error': 'таблицы не существует'},
            status=status.HTTP_400_BAD_REQUEST
        )
    return Response(
        {table: result},
        status=status.HTTP_200_OK
    )



@api_view(['DELETE'])
@permission_classes([IsAdminCustom])
def delete_table(request, table):
    '''удаление таблицы'''

    if not services.delete_table(table):
        return Response(
            {'error': 'Таблицы не существует'},
            status=status.HTTP_400_BAD_REQUEST
        )
    logger.info(f'table {table} deleted')
    return Response(
        {f'{table}': 'deleted'},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([IsAuthenticatedCustom])
def get_rows(request, table):
    '''получание колонок по определенным значениям столбцов'''

    data = SerializerQueryConditions(data=request.data)
    if data.is_valid():
        rows = services.get_rows(table, **data.data['conditions'])
        if rows:
            return Response(
                {'rows': rows},
                status=status.HTTP_200_OK
            )
    return Response(
        {'errors': 'данные не верны'},
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['POST'])
@permission_classes([IsAuthenticatedCustom])
def update_row(request, table):
    '''обновление значений'''

    data = SerializerColUpdate(data=request.data)
    if data.is_valid():
        pk = request.data.get('row_pk')
        updates = request.data.get('updates')
        if services.update_row(table, pk, **updates):
            logger.info(f'Updated table {table}, pk={pk}, data={updates}')
            return Response(
                {table: 'обновление успешно'},
                status=status.HTTP_200_OK
            )
    return Response(
        {'errors', 'данные не верны'},
        status=status.HTTP_400_BAD_REQUEST
    )