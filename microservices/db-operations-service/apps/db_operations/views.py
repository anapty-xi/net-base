import logging

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from .infrastructure.serializers.scv_serializer import CsvHandler
from .permissions import IsAdminCustom,IsAuthenticatedCustom
from .usecases import table_usecases
from .infrastructure.repository_manager import RepositoryManager
from rest_framework.permissions import AllowAny

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
        file = CsvHandler(request.data.get('file'))
    except TypeError:
        return Response(
            {'error': 'файл должен быть csv'},
            status=status.HTTP_400_BAD_REQUEST
        )
    analytics = request.data.get('in_analytics')
    infrastructure = RepositoryManager()
    usecase = table_usecases.CreateTable(infrastructure)
    logger.info(f'got file\n title={file.table_title}\ncols={file.cols}\nrows={file.rows}\nanal={analytics}')
    if not usecase.execute(file.table_title, file.cols, file.rows, analytics):
        logger.error(f'error ocured while {file.table_title} creating')
        return Response(
            {'error', 'Ошибка создании таблицы'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    logger.info(f'table {file.table_title} created')
    return Response(
        status=status.HTTP_201_CREATED
    )

@api_view(['GET'])
@permission_classes([IsAuthenticatedCustom]) 
def get_all_tabels(request):
    '''получание всех таблиц и их столбцов'''

    infrastucture = RepositoryManager()
    usecase = table_usecases.TableInfo(infrastucture)
    tables_info = usecase.execute()
    if not tables_info:
        logger.error('data base cannt get all table schemas')
        return Response(
            {'error': 'ошибка запроса к бд'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    logger.info(f'client got schemas:\n{tables_info}')
    return Response(
        tables_info,
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([IsAuthenticatedCustom])
def get_table(request, table):
    '''получание столбов конкретной таблицы'''

    infrastucture = RepositoryManager()
    usecase = table_usecases.TableInfo(infrastucture)
    table_info = usecase.execute(table)
    if not table_info:
        logger.error(f'table {table} doesn`t exists')
        return Response(
            {'error': 'таблицы не существует'},
            status=status.HTTP_400_BAD_REQUEST
        )
    logger.info(f'client got {table} schema:\n{table_info}')
    return Response(
        table_info,
        status=status.HTTP_200_OK
    )

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_table(request, table):
    '''удаление таблицы'''

    infrastucture = RepositoryManager()
    usecase = table_usecases.DeleteTable(infrastucture)
    if not usecase.execute(table):
        logger.error(f'table {table} doesn`t exists')
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

    data = request.data
    infrastucture = RepositoryManager()
    usecase = table_usecases.GetRows(infrastucture)
    rows = usecase.execute(table, data)
    if rows:
        logger.info(f'client got rows:\n{rows}')
        return Response(
            rows,
            status=status.HTTP_200_OK
        )
    logger.error(f'while get_rows error occured, input data:\ntable: {table}\nquery_params: {data}')
    return Response(
        {'errors': 'данные не верны'},
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['PATCH'])
@permission_classes([IsAuthenticatedCustom])
def update_row(request, table):
    '''обновление значений'''

    pk = request.data.get('row_pk')
    updates = request.data.get('updates')

    infrastucture = RepositoryManager()
    usecase = table_usecases.UpdateTable(infrastucture)
    try:
        usecase.execute(table, pk, updates)
        logger.info(f'Updated table {table}, pk={pk}, data={updates}')
        logger.info(f'successfuly updated row {pk}\nupdates: {updates}')
        return Response(
            {table: 'обновление успешно'},
            status=status.HTTP_200_OK
        )
    except ValueError as e:
        logger.error(f'while update_row error occured\ntable: {table}\npk: {pk}\nupdates: {updates}\n{e}')
        return Response(
            {'errors', 'данные не верны'},
            status=status.HTTP_400_BAD_REQUEST
        )