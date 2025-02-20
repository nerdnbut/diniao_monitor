# @Time    : 2024/8/24 17:37
# @Author  :      
from rest_framework import serializers
from .models import Server


class ServerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Server
        fields = ['id', 'name', 'ip_address', 'port', 'operating_system', 'status', 'user', 'password', 'created_at',
                  'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        server = Server(**validated_data)
        if password:
            server.set_password(password)
        server.save()
        return server

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
