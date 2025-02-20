from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from server_management.models import Server
from .models import ServerLog
from .serializers import ServerLogSerializer


class ServerLogPagination(PageNumberPagination):
    page_size = 20  # 默认每页显示的日志条数
    page_size_query_param = 'page_size'
    max_page_size = 100  # 最大分页条数


class ServerLogView(ListAPIView):
    serializer_class = ServerLogSerializer
    pagination_class = ServerLogPagination

    def get_queryset(self):
        server_id = self.kwargs['server_id']
        return ServerLog.objects.filter(server_id=server_id).order_by('-timestamp')

    def list(self, request, *args, **kwargs):
        server_id = kwargs.get('server_id')

        try:
            server = Server.objects.get(id=server_id)
            # 获取当前数据库中对应服务器的日志数量
            current_log_count = ServerLog.objects.filter(server_id=server_id).count()

            # 获取服务器的相关信息
            ip = server.ip_address
            port = server.port
            username = server.user
            password = server.get_password()

            # 从远程服务器获取日志文件内容
            logs = self.get_logs_from_server(ip, port, username, password, current_log_count)

            # 解析日志并保存到数据库
            self.save_logs_to_db(server, logs)

            # 获取日志并分页
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_paginated_response(self.get_serializer(page, many=True).data)
                return serializer

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        except Server.DoesNotExist:
            return Response({"error": "Server not found"}, status=status.HTTP_404_NOT_FOUND)

    def get_logs_from_server(self, ip, port, username, password, offset):
        import paramiko

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ip, port=port, username=username, password=password)

        # 定义可能存在的日志文件列表
        log_files = ['/var/log/syslog', '/var/log/messages']

        selected_log_file = None
        for log_file in log_files:
            _, stdout, stderr = ssh.exec_command(f'test -f {log_file} && echo "exists" || echo "not found"')
            result = stdout.read().decode('utf-8').strip()
            if result == "exists":
                selected_log_file = log_file
                break

        logs = ""
        if selected_log_file:
            # 从日志文件中获取从偏移量（offset）开始的新日志
            _, stdout, stderr = ssh.exec_command(f'tail -n +{offset + 1} {selected_log_file}')
            logs = stdout.read().decode('utf-8')
        else:
            logs = "服务器上未找到日志文件。"

        ssh.close()
        return logs

    def save_logs_to_db(self, server, logs):
        # 将获取到的日志解析并存入数据库
        log_entries = []
        existing_logs = ServerLog.objects.filter(server=server)

        for line in logs.splitlines():
            timestamp = self.parse_timestamp(line)
            message = line
            log_level = self.parse_log_level(line)

            # 检查是否已经存在相同的日志条目
            if not existing_logs.filter(timestamp=timestamp, message=message).exists():
                log_entries.append(ServerLog(
                    server=server,
                    log_level=log_level,
                    message=message,
                    timestamp=timestamp
                ))

        if log_entries:
            ServerLog.objects.bulk_create(log_entries)

    def parse_log_level(self, line):
        # 解析日志行中的日志等级
        # 假设日志行以[INFO]、[ERROR]等开头
        if '[ERROR]' in line:
            return 'ERROR'
        elif '[INFO]' in line:
            return 'INFO'
        elif '[WARNING]' in line:
            return 'WARNING'
        else:
            return 'UNKNOWN'

    def parse_timestamp(self, line):
        # 解析日志行中的时间戳
        import datetime
        if 'T' in line and '+' in line:
            timestamp_str = line.split(' ')[0]
            dt = datetime.datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%f%z')
        else:
            timestamp_str = line[:15]
            dt = datetime.datetime.strptime(timestamp_str, '%b %d %H:%M:%S')
            dt = dt.replace(year=datetime.datetime.now().year)
        formatted_timestamp = dt.strftime('%Y-%m-%d %H:%M')
        return formatted_timestamp
