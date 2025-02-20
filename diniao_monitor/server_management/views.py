from rest_framework import viewsets, status
from .models import Server
from .serializers import ServerSerializer
from django.http import JsonResponse
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .server_resource import cpu, mem, swp, Network


class ServerViewSet(viewsets.ModelViewSet):
    serializer_class = ServerSerializer
    queryset = Server.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Server.objects.filter(owner=user)

    def perform_create(self, serializer):  # 输出前端传递的数据
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["get"])
    def monitor(self, request, pk=None):
        server = self.get_object()
        # 获取服务器的IP、用户名、密码、端口
        ip = server.ip_address
        user = server.user
        password = server.get_password()
        port = server.port

        # 使用Fabric获取服务器资源信息
        try:
            result = self.get_server_info(ip, user, password, port)
            return JsonResponse(result, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_server_info(self, ip, username, password, port):
        from fabric import Connection
        # 使用Fabric连接服务器
        conn = Connection(host=ip, user=username, port=port, connect_kwargs={"password": password})

        try:
            # 获取资源使用情况
            cpu_usage = cpu.run_cpu(ip, username, password, port)
            mem_usage = mem.run_mem(ip, username, password, port)
            swp_usage = swp.run_swp(ip, username, password, port)
            network_usage = Network.run_network(ip, username, password, port)

            # 获取并格式化磁盘使用情况
            disk_usage_raw = conn.run('df -h').stdout.strip()
            disk_usage_lines = disk_usage_raw.splitlines()
            disk_usage_headers = disk_usage_lines[0].split()
            disk_usage_data = []

            for line in disk_usage_lines[1:]:
                disk_info = line.split()
                disk_usage_data.append(dict(zip(disk_usage_headers, disk_info)))

            system_info = conn.run('uname -a').stdout.strip()

            # 组织返回结果
            return {
                "cpu": cpu_usage,
                "mem": mem_usage,
                "swp": swp_usage,
                "network": network_usage,
                "disk": disk_usage_data,
                "system": system_info
            }
        finally:
            conn.close()