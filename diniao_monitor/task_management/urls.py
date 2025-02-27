from django.urls import path
from .views import create_scheduled_task, list_scheduled_tasks, upload_script, delete_scheduled_task

urlpatterns = [
    path('create-task/', create_scheduled_task),
    path('tasks/', list_scheduled_tasks),
    path('upload-script/', upload_script),
    path('tasks/<int:task_id>/', delete_scheduled_task, name='delete_scheduled_task'),
] 