import logging

from django.http import HttpResponse

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny

from .infrastructure.serializers.xlsx_serializer import XLSXSerializer
from .infrastructure.repository_manager import RepositoryManager

from .permissions import IsAdminCustom,IsAuthenticatedCustom

from .usecases import table_usecases



logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAdminCustom])
@parser_classes([MultiPartParser, FormParser])
def create_table(request):
    '''создание и заполнение таблицы по переданному файлу'''

    if 'file' not in request.data:
        logger.error('create_table/ no file')
        return Response(
            {'error': 'xlsx файл необходим'},
            status=status.HTTP_400_BAD_REQUEST
        )
    serializer = XLSXSerializer()
    try:
        file = serializer.unserialize(request.data.get('file'))
    except TypeError:
        logger.error('create_table/ file is not xlsx ')
        return Response(
            {'error': 'файл должен быть xlsx'},
            status=status.HTTP_400_BAD_REQUEST
        )
    analytics = request.data.get('in_analytics')
    infrastructure = RepositoryManager()
    usecase = table_usecases.CreateTable(infrastructure)
    logger.info(f'create_table/ got file\n title={file['title']}\ncols={file['cols']}\nanal={analytics}')
    try:
        if not usecase.execute(file['title'], file['cols'], file['rows'], analytics):
            logger.error(f'create_table/ error ocured while {file['title']} creating')
            return Response(
                {'error', 'Ошибка создании таблицы'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        logger.info(f'create_table/ table {file['title']} created')
        return Response(
            status=status.HTTP_201_CREATED
        )
    except Exception as e:
        logger.error(f'create_table/ {e}')
        return Response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET'])
@permission_classes([IsAuthenticatedCustom]) 
def get_all_tabels(request):
    '''получание всех таблиц и их столбцов'''

    infrastucture = RepositoryManager()
    usecase = table_usecases.TableInfo(infrastucture)
    tables_info = usecase.execute()
    if not tables_info:
        logger.error('get_all_tables/ data base cannt get all table schemas')
        return Response(
            {'error': 'ошибка запроса к бд'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    logger.info(f'get_all_tables/ client got schemas:\n{tables_info}')
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
        logger.error(f'get_table/ table {table} doesn`t exists')
        return Response(
            {'error': 'таблицы не существует'},
            status=status.HTTP_400_BAD_REQUEST
        )
    logger.info(f'get_table/ client got {table} schema:\n{table_info}')
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
        logger.error(f'delete_table/ table {table} doesn`t exists')
        return Response(
            {'error': 'Таблицы не существует'},
            status=status.HTTP_400_BAD_REQUEST
        )
    logger.info(f'delete_table/ table {table} deleted')
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
        logger.info(f'get_rows/ client got rows {len(rows)}')
        return Response(
            rows,
            status=status.HTTP_200_OK
        )
    logger.error(f'get_rows/ while get_rows error occured, input data:\ntable: {table}\nquery_params: {data}')
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
        logger.info(f'update_row/ successfuly updated row {pk}\nupdates: {updates}')
        return Response(
            {table: 'обновление успешно'},
            status=status.HTTP_200_OK
        )
    except ValueError as e:
        logger.error(f'update_row/ while update_row error occured\ntable: {table}\npk: {pk}\nupdates: {updates}\n{e}')
        return Response(
            {'errors', 'данные не верны'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
@api_view(['GET'])
@permission_classes([IsAuthenticatedCustom])
def table_file(request, table):
    '''
    Получение файла xlsx для таблицы
    '''
    try:
        schema_infrastructure = RepositoryManager()
        schema_usecase = table_usecases.TableInfo(schema_infrastructure)
        schema = schema_usecase.execute(table)

        rows_infrastructure = RepositoryManager()
        rows_usecase = table_usecases.GetRows(rows_infrastructure)
        rows = rows_usecase.execute(table, None)
    except Exception as e:
        logger.error(f'table_file/ while getting table schema error occurred: {e}')
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    serializer = XLSXSerializer()
    try:
        xlsx_table = serializer.serialize(table, schema[table], rows)
    except Exception as e:
        logger.error(f'table_file/ while file serializing error occurred: {e}')
        return Response(
            {'error': f'ошибка сериализации в файл: {e}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    response = HttpResponse(
        xlsx_table,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{table}.xlsx"'
    logger.info(f'table_file/ client got table file: {table}')
    return response

