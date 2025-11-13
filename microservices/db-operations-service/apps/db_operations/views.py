from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .tasks import create_table
from .serializers import SerializerTableCreate

@api_view(['POST'])
@permission_classes([AllowAny]) #заменить на админа
def simple_test(request):
    if not SerializerTableCreate(data=request.data).is_valid():
        return Response (
            status=status.HTTP_400_BAD_REQUEST
        )
    
    table_title = request.data.get('table_title')
    cols = request.data.get('cols').split(';')
    rows = request.data.get('rows')

    create_table.delay(table_title, cols)
    return Response (
        {'task': 'ready'},
        status=status.HTTP_200_OK
    )



