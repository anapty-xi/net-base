from django.contrib import admin
from django.urls import path
from django.urls import include
from django.http import HttpResponse

def health_chek(request):
    return HttpResponse('OK', status=200)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_chek),
    path('analytics/', include('apps.analytics.urls'))
]
