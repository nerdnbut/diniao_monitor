# @Time    : 2024/8/30 20:12
# @Author  :      
# server_management/routing.py

from django.urls import re_path
from server_management.server_resource.consumers import SSHConsumer

websocket_urlpatterns = [
    re_path(r'ws/ssh/$', SSHConsumer.as_asgi()),
]


