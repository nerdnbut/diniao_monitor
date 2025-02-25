import paramiko

def ssh_connect(hostname, username, password, port=22):
    """
    建立SSH连接
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        hostname=hostname,
        port=port,
        username=username,
        password=password
    )
    return ssh 