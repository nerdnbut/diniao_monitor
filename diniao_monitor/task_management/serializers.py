from rest_framework import serializers
from .models import ScheduledTask

class ScheduledTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledTask
        fields = '__all__' 