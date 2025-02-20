# @Time    : 2024/9/2 21:35
# @Author  :      
from django.urls import path
from .views import ServerLogView

urlpatterns = [
    path('log/<int:server_id>/', ServerLogView.as_view(), name='server-log'),
]
