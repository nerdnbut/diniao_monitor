from django.db import models
from server_management.models import Server


class ServerLog(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='log_entries')
    timestamp = models.DateTimeField()
    log_level = models.CharField(max_length=10)
    message = models.TextField()

    def __str__(self):
        return f"{self.timestamp} - {self.log_level} - {self.server.name}"

    class Meta:
        unique_together = ('server', 'timestamp')
