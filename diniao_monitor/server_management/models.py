# server_management/models.py

from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet



class Server(models.Model):
    """服务器模型"""
    id = models.AutoField(primary_key=True, verbose_name="ID")
    name = models.CharField(max_length=100, verbose_name="服务器名称")
    ip_address = models.GenericIPAddressField(verbose_name="IP 地址")
    port = models.PositiveIntegerField(verbose_name="端口号")
    operating_system = models.CharField(max_length=100, verbose_name="操作系统")
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('maintenance', 'Maintenance'),
        ],
        default='active',
        verbose_name="状态"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建日期")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日期")
    # 关联User表, 用于关联服务器所属用户
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='servers',
        verbose_name="拥有者"
    )
    # 用户名字段
    user = models.CharField(max_length=100, null=True, blank=True, verbose_name="用户名")
    encrypted_password = models.BinaryField(null=True, blank=True, verbose_name="加密密码")

    def _get_fernet(self):
        """延迟加载 Fernet 加密器"""
        return Fernet(settings.ENCRYPTION_KEY)

    def set_password(self, raw_password):
        if raw_password:
            fernet = self._get_fernet()
            # 确保加密前后编码一致
            self.encrypted_password = fernet.encrypt(raw_password.encode('utf-8'))
        else:
            self.encrypted_password = None

    def get_password(self):
        if self.encrypted_password:
            fernet = self._get_fernet()
            # 确保解密后编码一致
            return fernet.decrypt(self.encrypted_password).decode('utf-8')
        return None

    def __str__(self):
        return self.name
        # return f"服务器id: {self.id}"
