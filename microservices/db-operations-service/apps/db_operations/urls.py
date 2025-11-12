from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.simple_test, name='create_table')
]