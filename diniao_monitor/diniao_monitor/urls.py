from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('User.urls')),  # 引入User应用的路由
    path('api/', include('server_management.urls')),  # 引入server_management应用的路由
    path('api/', include('log_management.urls')),
    path('api/', include('alarm_set.urls')),
    path('api/', include('file_management.urls')),  # 添加文件管理的路由
    path('api/', include('task_management.urls')),  # 添加任务管理的路由
]
