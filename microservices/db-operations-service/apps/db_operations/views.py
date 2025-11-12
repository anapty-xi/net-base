from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .tasks import create_table

@api_view(['POST'])
@permission_classes([AllowAny])
def simple_test(request):
    table_name = request.data.get('table_name')
    cols = request.data.get('cols').split(';')
    create_table.delay(table_name, cols)
    return Response (
        {'task': 'ready'},
        status=status.HTTP_200_OK
    )



