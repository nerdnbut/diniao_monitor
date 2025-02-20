from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Server
from .forms import ServerAdminForm


# 在django后端绑定自定义的服务器信息管理表单
@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    form = ServerAdminForm
    list_display = ('name', 'ip_address', 'port', 'operating_system', 'status', 'owner', 'created_at', 'updated_at')
    search_fields = ('name', 'ip_address', 'operating_system', 'owner__email')
    list_filter = ('status', 'created_at', 'owner')
    readonly_fields = ('created_at', 'updated_at')
