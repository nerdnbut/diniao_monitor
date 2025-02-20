# @Time    : 2024/9/2 21:55
# @Author  :      
from rest_framework import serializers
from .models import ServerLog


class ServerLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerLog
        fields = '__all__'  # 或者明确指定字段，比如 ['timestamp', 'log_level', 'message']
