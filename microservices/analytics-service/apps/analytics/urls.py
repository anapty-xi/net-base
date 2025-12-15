from django.urls import path
from . import views

urlpatterns = [
    path('tables_report/', views.get_report)
]