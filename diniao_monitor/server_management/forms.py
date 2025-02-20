# @Time    : 2024/8/24 10:57
# @Author  :      
from django import forms
from .models import Server


# 定义表单处理密码字段，为了让admin后台管理页面可以修改密码，并可以实现在后端管理界面输入密码实现密码自动加密
class ServerAdminForm(forms.ModelForm):
    password = forms.CharField(required=False, widget=forms.PasswordInput, label="密码")

    class Meta:
        model = Server
        fields = '__all__'

    def save(self, commit=True):
        server = super().save(commit=False)
        raw_password = self.cleaned_data.get('password')
        if raw_password:
            server.set_password(raw_password)
        if commit:
            server.save()
        return server
