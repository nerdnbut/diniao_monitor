# @Time    : 2024/8/28 14:55
# @Author  :      
import re
from fabric import Connection
from fabric import task


def parse_meminfo(content):
    """解析 /proc/meminfo 文件内容"""
    mem_info = {'totalMem': 0, 'freeMem': 0}
    lines = content.splitlines()
    for line in lines:
        if line.startswith("MemTotal:"):
            mem_info['totalMem'] = int(re.search(r'\d+', line).group())
        elif line.startswith("MemFree:"):
            mem_info['freeMem'] = int(re.search(r'\d+', line).group())
    return mem_info


def mem_usage(mem_info):
    """计算内存使用率"""
    total_mem = mem_info['totalMem']
    free_mem = mem_info['freeMem']
    used_mem = total_mem - free_mem
    usage_rate = (used_mem / total_mem) * 100.0
    return usage_rate


@task
def fetch_meminfo(c):
    """从远程主机获取 /proc/meminfo 文件内容"""
    result = c.run('cat /proc/meminfo', hide=True)
    return result.stdout


def run_mem(host, user, connect_kwargs, port):
    # 连接到远程主机
    conn = Connection(host=host, user=user, port=port, connect_kwargs={"password": connect_kwargs})

    # 获取远程主机的内存信息
    meminfo_content = fetch_meminfo(conn)

    # 解析内存信息
    mem_info = parse_meminfo(meminfo_content)

    # 计算内存使用率
    usage_rate = mem_usage(mem_info)

    # 输出内存使用率
    print(f"Memory Usage: {usage_rate:.2f}%")
    return usage_rate


