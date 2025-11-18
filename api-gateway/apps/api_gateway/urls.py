from django.urls import re_path
from . import views


urlpatterns = [
    re_path(r'^db/.*', views.proxy_view, name='db-proxy'),
    re_path(r'^user/.*', views.proxy_view, name='user-proxy'),
]