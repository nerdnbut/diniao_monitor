# @Time    : 2025/2/10 21:05
# @Author  :      
from rest_framework import serializers
from .models import AlarmTask
from server_management.models import Server


class AlarmTaskSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='serverId.name', read_only=True)

    class Meta:
        model = AlarmTask
        fields = ['id', 'serverId', 'alarmType', 'alarmLevel', 'threshold', 'current_value', 'status', 'message',
                  'created_at', 'updated_at', 'name']


class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = ['id', 'name']
