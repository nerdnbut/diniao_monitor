import paramiko
import socket
import sys
import msvcrt
import select


def remote_terminal(ip, username, password, port=22, timeout=1, prompt_list=['#', '$']):
    # 创建SSH客户端
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, port, username, password)

    # 打开一个shell通道
    channel = ssh.invoke_shell()
    channel.settimeout(timeout)

    buffer = ""
    while True:
        # 检查是否有本地输入（用户输入）
        if msvcrt.kbhit():
            user_input = msvcrt.getch()

            if user_input == b'\x1b':  # ESC key for Vim mode
                channel.send(user_input)
            elif user_input == b'\t':  # Tab for autocomplete
                channel.send(user_input)
            elif user_input == b'\x03':  # Ctrl+C to exit
                break
            elif user_input == b'q':  # 'q' to quit interactive commands like top
                channel.send(user_input)
            else:
                channel.send(user_input)

        # 检查是否有远程输出（服务器返回的结果）
        if channel.recv_ready():
            output = channel.recv(1024).decode('utf-8')
            buffer += output
            sys.stdout.write(output)
            sys.stdout.flush()

            # 检查是否收到提示符
            if any(prompt in buffer for prompt in prompt_list):
                buffer = ""  # 清空缓冲区

    # 关闭连接
    channel.close()
    ssh.close()


# 使用示例
remote_terminal('192.168.113.80', 'root', '123456')
