from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_table, name='create_table'),
    path('get_table_info/', views.get_all_tabels, name='get_all_tables'),
    path('get_table_info/<str:table>/', views.get_table, name='get_all_tables'),
    path('delete/<str:table>/', views.delete_table, name='delete_table'),
    path('get_rows/<str:table>/', views.get_rows, name='get_rows'),
    path('update_row/<str:table>/', views.update_row, name='update_row')
]