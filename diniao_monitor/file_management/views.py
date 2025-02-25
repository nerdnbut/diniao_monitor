from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from server_management.models import Server
from server_management.server_resource.server_resource import ssh_connect
import os
import paramiko
from django.http import FileResponse
from rest_framework.permissions import IsAuthenticated
import stat  # 添加这个导入
import uuid

class FileManagementViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list_files(self, request, server_id):
        try:
            server = Server.objects.get(id=server_id)
            path = request.GET.get('path', '/')
            
            ssh = ssh_connect(server.ip_address, server.user, server.get_password(), server.port)
            sftp = ssh.open_sftp()
            
            files = []
            for entry in sftp.listdir_attr(path):
                file_type = 'directory' if stat.S_ISDIR(entry.st_mode) else 'file'
                files.append({
                    'name': entry.filename,
                    'type': file_type,
                    'size': entry.st_size,
                    'modifiedTime': entry.st_mtime,
                    'path': os.path.join(path, entry.filename).replace('\\', '/')
                })
            
            sftp.close()
            ssh.close()
            return Response(files)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def content(self, request, server_id):
        try:
            server = Server.objects.get(id=server_id)
            path = request.GET.get('path')
            
            ssh = ssh_connect(server.ip_address, server.user, server.get_password(), server.port)
            sftp = ssh.open_sftp()
            
            with sftp.file(path, 'r') as f:
                content = f.read().decode('utf-8')
            
            sftp.close()
            ssh.close()
            return Response({'content': content})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def save(self, request, server_id):
        try:
            server = Server.objects.get(id=server_id)
            path = request.data.get('path')
            content = request.data.get('content')
            
            ssh = ssh_connect(server.ip_address, server.user, server.get_password(), server.port)
            sftp = ssh.open_sftp()
            
            with sftp.file(path, 'w') as f:
                f.write(content)
            
            sftp.close()
            ssh.close()
            return Response({'message': 'File saved successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def delete(self, request, server_id):
        try:
            server = Server.objects.get(id=server_id)
            path = request.GET.get('path')
            
            ssh = ssh_connect(server.ip_address, server.user, server.get_password(), server.port)
            sftp = ssh.open_sftp()
            
            sftp.remove(path)
            
            sftp.close()
            ssh.close()
            return Response({'message': 'File deleted successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def download(self, request, server_id):
        temp_file = None
        ssh = None
        sftp = None
        try:
            server = Server.objects.get(id=server_id)
            path = request.GET.get('path')
            
            ssh = ssh_connect(server.ip_address, server.user, server.get_password(), server.port)
            sftp = ssh.open_sftp()
            
            # 创建临时目录
            os.makedirs('/tmp', exist_ok=True)
            
            # 使用唯一文件名避免冲突
            temp_filename = f"{uuid.uuid4()}_{os.path.basename(path)}"
            local_path = os.path.join('/tmp', temp_filename)
            
            # 下载文件
            sftp.get(path, local_path)
            
            # 打开文件并读取内容
            temp_file = open(local_path, 'rb')
            response = FileResponse(temp_file)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(path)}"'
            
            # 确保文件在响应完成后被删除
            response._resource_closers.append(lambda: self._cleanup_temp_file(local_path, temp_file))
            
            return response
            
        except Exception as e:
            # 发生错误时清理资源
            if temp_file:
                temp_file.close()
            if sftp:
                sftp.close()
            if ssh:
                ssh.close()
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def _cleanup_temp_file(self, path, file_obj):
        """清理临时文件的辅助方法"""
        try:
            if file_obj:
                file_obj.close()
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass  # 忽略清理过程中的错误

    @action(detail=True, methods=['post'])
    def upload(self, request, server_id):
        try:
            server = Server.objects.get(id=server_id)
            path = request.data.get('path') + '/'  # 上传的目标路径
            file = request.FILES.get('file')  # 获取上传的文件
            if not file:
                return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

            ssh = ssh_connect(server.ip_address, server.user, server.get_password(), server.port)
            sftp = ssh.open_sftp()
            
            # 将文件写入目标路径
            with sftp.file(os.path.join(path, file.name), 'wb') as f:
                f.write(file.read())
            
            sftp.close()
            ssh.close()
            return Response({'message': 'File uploaded successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)