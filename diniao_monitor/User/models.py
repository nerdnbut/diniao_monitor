from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class MyUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError('The Username field is required')

        user = self.model(username=username)
        # 密码加密
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None):
        user = self.create_user(username, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    # ID主键自增长
    id = models.AutoField(primary_key=True, auto_created=True)
    # 邮箱字段
    email = models.EmailField(max_length=255, unique=True, blank=False, null=False)
    username = models.CharField(max_length=255, blank=False, null=False)
    password = models.CharField(max_length=255, blank=False, null=False)
    objects = MyUserManager()

    USERNAME_FIELD = 'email'
