import json
import paramiko
import threading
import time
from channels.generic.websocket import WebsocketConsumer


class SSHConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ssh_client = None
        self.channel = None
        self.is_active = True
        self.output_thread = None

    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        self.is_active = False
        if self.channel:
            self.channel.close()
        if self.ssh_client:
            self.ssh_client.close()
        if self.output_thread and self.output_thread.is_alive():
            self.output_thread.join()

    def receive(self, text_data):
        print(f"接收到的消息：{text_data}")  # 添加调试信息
        data = json.loads(text_data)
        server_id = data.get('server_id')

        if server_id:
            server_info = self.get_server_info(server_id)
            if server_info:
                self.establish_ssh_connection(server_info)
            else:
                self.send(text_data=json.dumps({"error": "Server not found"}))
        else:
            input_data = data.get('input')
            print(f"处理的输入数据：{input_data}")  # 添加调试信息
            if input_data is not None:
                if input_data.strip() == '':
                    # 处理空输入
                    # self.send(text_data=json.dumps({"error": "Invalid input1"}))
                    self.send_input('\n')  # 发送换行符到SSH通道
                else:
                    print(f"有效输入：{input_data}，通道：{self.channel}")
                    self.send_input(input_data)
            else:
                print(f"收到无效输入: {input_data}")
                self.send(text_data=json.dumps({"error": "Invalid input2"}))

    def get_server_info(self, server_id):
        from server_management.models import Server
        try:
            server = Server.objects.filter(id=server_id).first()
            if server is None:
                print(f"服务器 ID {server_id} 不存在")
                return None
            return {
                'ip': server.ip_address,
                'port': server.port,
                'username': server.user,
                'password': server.get_password()
            }
        except Exception as e:
            print(f"获取服务器信息错误：{e}")
            return None

    def establish_ssh_connection(self, server_info):
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(
                hostname=server_info['ip'],
                port=server_info['port'],
                username=server_info['username'],
                password=server_info['password']
            )
            self.channel = self.ssh_client.invoke_shell()
            self.is_active = True
            self.output_thread = threading.Thread(target=self.read_output)
            self.output_thread.start()
            self.send(text_data=json.dumps({"status": "Connected"}))
        except Exception as e:
            print(f"错误信息：{e}")
            self.send(text_data=json.dumps({"error": str(e)}))

    def send_input(self, input_data):
        if self.channel:
            self.channel.send(input_data)

    def read_output(self):
        buffer = ""
        prompt_list = ['#', '$', '>']  # 示例提示符
        while self.is_active:
            if self.channel.recv_ready():
                output = self.channel.recv(1024).decode('utf-8')
                buffer += output
                self.send(text_data=json.dumps({"output": output}))

                if any(prompt in buffer for prompt in prompt_list):
                    buffer = ""

            time.sleep(0.1)
        self.disconnect(None)
