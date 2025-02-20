# @Time    : 2025/2/10 21:07
# @Author  :      
from django.urls import path
from .views import AlarmTaskCreateView, AlarmTaskListView, AlarmTaskDeleteView, AlarmTaskUpdateView


urlpatterns = [
    path('alarm-task/', AlarmTaskCreateView.as_view(), name='alarm-task-create'),
    path('alarms/', AlarmTaskListView.as_view(), name='alarm_task_list'),
    path('alarms/delete/<int:pk>/', AlarmTaskDeleteView.as_view(), name='delete_alarm_task'),
    path('alarms/update/<int:pk>/', AlarmTaskUpdateView.as_view(), name='update_alarm_task'),
]