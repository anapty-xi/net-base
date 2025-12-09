import logging

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from .infrastructure.serializers.drf_serializers.serializers import SerializerQueryConditions, SerializerColUpdate
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
        file = CsvHandler(request.data['file'])
    except TypeError:
        return Response(
            {'error': 'файл должен быть csv'},
            status=status.HTTP_400_BAD_REQUEST
        )
    analytics = request.data.get('analytics')
    infrastructure = RepositoryManager()
    usecase = table_usecases.CreateTable(infrastructure)
    if not usecase.execute(file.table_title, file.cols, file.rows, analytics):
        return Response(
            {'error', 'Ошибка создании таблицы'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    return Response(
        status=status.HTTP_201_CREATED
    )

@api_view(['GET'])
@permission_classes([IsAuthenticatedCustom]) 
def get_all_tabels(request):
    '''получание всех таблиц и их столбцов'''

    infrastucture = RepositoryManager()
    usecase = table_usecases.TableInfo(infrastucture)
    result = usecase.execute()
    if not result:
        return Response(
            {'error': 'ошибка запроса к бд'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    return Response(
        result,
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
        return Response(
            {'error': 'таблицы не существует'},
            status=status.HTTP_400_BAD_REQUEST
        )
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

    data = request.data
    infrastucture = RepositoryManager()
    usecase = table_usecases.GetRows(infrastucture)
    rows = usecase.execute(table, data)
    if rows:
        return Response(
            rows,
            status=status.HTTP_200_OK
        )
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
    if usecase.execute(table, pk, updates):
        logger.info(f'Updated table {table}, pk={pk}, data={updates}')
        return Response(
            {table: 'обновление успешно'},
            status=status.HTTP_200_OK
        )
    return Response(
        {'errors', 'данные не верны'},
        status=status.HTTP_400_BAD_REQUEST
    )