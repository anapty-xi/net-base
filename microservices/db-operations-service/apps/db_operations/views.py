import logging

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from . import tasks
from .serializers import SerializerTableCreate, SerializerQueryConditions, SerializerColUpdate
from . import services
from .permissions import IsAdminCustom,IsAuthenticatedCustom

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAdminCustom])
def create_table(request):
    '''создание и заполнение таблицы по переданному csv файлу'''

    data = SerializerTableCreate(data=request.data)
    if not data.is_valid():
        logger.error('invalid data')
        return Response (
            {'errors': data.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    table_title = request.data.get('table_title')
    cols = request.data.get('cols').split(';')
    rows = request.data.get('rows')

    tasks.create_table.delay(table_title, cols, rows)
    logger.info('Table creating')
    return Response (
        {'task': 'ready'},
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
    json_res = {}
    for table, col in result:
        if table in json_res.keys():
            json_res[table].append(col)
        else:
            json_res[table]=[col]

    return Response(
        {'tabels': json_res},
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
    cols = [col[0] for col in result]
    return Response(
        {table: cols},
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


@api_view(['GET'])
@permission_classes([IsAuthenticatedCustom])
def get_rows(request, table):
    '''получание колонок по определенным значениям столбцов'''

    data = SerializerQueryConditions(data=request.data)
    if data.is_valid():
        resp = services.get_rows(table, **request.data.get('conditions'))
        if resp:
            return Response(
                {'cols': resp},
                status=status.HTTP_200_OK
            )
    return Response(
        {'errors': 'Данные не верны'},
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['PATCH'])
@permission_classes([IsAuthenticatedCustom])
def update_row(request, table):
    '''обновление значений'''

    data = SerializerColUpdate(data=request.data)
    if data.is_valid():
        pk = request.data.get('row_pk')
        updates = request.data.get('updates')
        resp = services.update_row(table, pk, **updates)
        if resp:
            logger.info(f'Updated table {table}, pk={pk}, data={updates}')
            return Response(
                {table: 'обновление успешно'},
                status=status.HTTP_200_OK
            )
    return Response(
        {'errors', 'данные не верны'},
        status=status.HTTP_400_BAD_REQUEST
    )