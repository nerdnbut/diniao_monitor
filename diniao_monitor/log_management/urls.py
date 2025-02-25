# @Time    : 2024/9/2 21:35
# @Author  :      
from django.urls import path
from .views import ServerLogView, DeleteLogView, DownloadLogView

urlpatterns = [
    path('log/<int:server_id>/', ServerLogView.as_view(), name='server-logs'),
    path('log/<int:server_id>/<int:log_id>/', DeleteLogView.as_view(), name='delete-log'),
    path('log/<int:server_id>/<int:log_id>/download/', DownloadLogView.as_view(), name='download-log'),
]
