from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_table, name='create_table'),
    path('get_all_tabels/', views.view_all_tables, name='get_all_tables'),
    path('delete/<str:table>/', views.delete_table, name='delete_table'),
]