# @Time    : 2024/8/28 15:00
# @Author  :      
import re
from fabric import Connection
from fabric import task


def parse_df_output(content):
    """解析 df 命令输出"""
    disk_info = {'total': 0, 'used': 0}
    lines = content.splitlines()
    for line in lines[1:]:  # 跳过标题行
        fields = line.split()
        if len(fields) >= 5:
            # 将大小转换为KB
            total = int(fields[1]) * 1024
            used = int(fields[2]) * 1024
            disk_info['total'] += total
            disk_info['used'] += used
    return disk_info


def disk_usage(disk_info):
    """计算磁盘使用率"""
    total = disk_info['total']
    used = disk_info['used']
    usage_rate = (used / total) * 100.0 if total > 0 else 0
    return usage_rate


@task
def fetch_df(c):
    """从远程主机获取 df 命令输出"""
    result = c.run('df -k', hide=True)
    return result.stdout


def run_swp(host, user, connect_kwargs, port):
    # 连接到远程主机
    conn = Connection(host=host, user=user, port=port, connect_kwargs={"password": connect_kwargs})

    # 获取远程主机的磁盘信息
    df_content = fetch_df(conn)

    # 解析磁盘信息
    disk_info = parse_df_output(df_content)

    # 计算磁盘使用率
    usage_rate = disk_usage(disk_info)

    # 输出磁盘使用率
    print(f"Disk Usage: {usage_rate:.2f}%")
    return usage_rate


