from django.db import models
from server_management.models import Server

class FileOperation(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    path = models.CharField(max_length=1024)
    operation_type = models.CharField(max_length=20)  # list, read, write, delete
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)  # success, failed
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']