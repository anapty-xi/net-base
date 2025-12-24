from django.contrib import admin
from django.urls import path
from django.urls import include
from rest_framework.response import Response
from rest_framework import status

def health_chek(request):
    return Response(
        {'status': 'healthy',
        'service': 'user-service'},
        status=status.HTTP_200_OK
    )

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_chek),
    path('user/', include('apps.users.urls')),
]
    

