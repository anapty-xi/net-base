from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .tasks import create_table
from .serializers import SerializerTableCreate
from . import services

@api_view(['POST'])
@permission_classes([AllowAny]) #заменить на админа
def create_table(request):
    data = SerializerTableCreate(data=request.data)
    if not data.is_valid():
        return Response (
            {'errors': data.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    table_title = request.data.get('table_title')
    cols = request.data.get('cols').split(';')
    rows = request.data.get('rows')

    create_table.delay(table_title, cols, rows)
    return Response (
        {'task': 'ready'},
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def view_all_tables(request):
    result = services.get_tables_with_cols()
    return Response(
        {'tabels': str(result)},
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_table(request, table):
    if not services.delete_table(table):
        return Response(
            {'error': 'Таблицы не существует'},
            status=status.HTTP_400_BAD_REQUEST
        )
    return Response(
        {f'{table}': 'deleted'},
        status=status.HTTP_200_OK
    )
