from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import AlarmTask
from server_management.models import Server
from .serializers import AlarmTaskSerializer, ServerSerializer


class AlarmTaskCreateView(APIView):
    def post(self, request):
        """处理报警任务创建请求"""
        # 使用AlarmTaskSerializer序列化报警任务数据
        serializer = AlarmTaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # 保存报警任务
            return Response({"message": "报警任务已创建"}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)  # 打印错误，查看问题原因
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AlarmTaskListView(APIView):
    permission_classes = [IsAuthenticated]  # 仅允许认证用户访问

    def get(self, request):
        # 假设每个用户只能看到自己管理的服务器上的报警任务
        user_servers = request.user.servers.all()  # 获取用户拥有的服务器
        alarms = AlarmTask.objects.filter(serverId__in=user_servers)
        serializer = AlarmTaskSerializer(alarms, many=True)
        return Response(serializer.data)


class AlarmTaskDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            alarm = AlarmTask.objects.get(id=pk)
            alarm.delete()
            return Response({"message": "报警任务已删除"}, status=status.HTTP_204_NO_CONTENT)
        except AlarmTask.DoesNotExist:
            return Response({"error": "报警任务不存在"}, status=status.HTTP_404_NOT_FOUND)


class AlarmTaskUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            alarm = AlarmTask.objects.get(id=pk)

            # 使用传递的数据更新，未修改字段则使用原值
            updated_data = request.data.copy()  # 复制传递的数据

            # 如果没有传递 alarmLevel 或者传递了空字符串，就用原值
            if 'alarmLevel' not in updated_data or updated_data['alarmLevel'] == "":
                updated_data['alarmLevel'] = alarm.alarmLevel  # 保留原值

            # 如果没有传递 threshold 或者传递了空字符串，就用原值
            if 'threshold' not in updated_data or updated_data['threshold'] == "":
                updated_data['threshold'] = alarm.threshold  # 保留原值

            serializer = AlarmTaskSerializer(alarm, data=updated_data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                print(serializer.errors)  # 输出错误
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except AlarmTask.DoesNotExist:
            return Response({"error": "报警任务不存在"}, status=status.HTTP_404_NOT_FOUND)


