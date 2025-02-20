# @Time    : 2024/8/28 15:00
# @Author  :      
import re
from fabric import Connection
from fabric import task


def parse_swapinfo(content):
    """解析 /proc/meminfo 文件中的交换空间信息"""
    swap_info = {'totalSwap': 0, 'usedSwap': 0}
    lines = content.splitlines()
    for line in lines:
        if line.startswith("SwapTotal:"):
            swap_info['totalSwap'] = int(re.search(r'\d+', line).group())
        elif line.startswith("SwapFree:"):
            swap_info['freeSwap'] = int(re.search(r'\d+', line).group())

    swap_info['usedSwap'] = swap_info['totalSwap'] - swap_info.get('freeSwap', 0)
    return swap_info


def swap_usage(swap_info):
    """计算交换空间使用率"""
    total_swap = swap_info['totalSwap']
    used_swap = swap_info['usedSwap']
    usage_rate = (used_swap / total_swap) * 100.0 if total_swap > 0 else 0
    return usage_rate


@task
def fetch_meminfo(c):
    """从远程主机获取 /proc/meminfo 文件内容"""
    result = c.run('cat /proc/meminfo', hide=True)
    return result.stdout


def run_swp(host, user, connect_kwargs, port):

    # 连接到远程主机
    conn = Connection(host=host, user=user, port=port, connect_kwargs={"password": connect_kwargs})

    # 获取远程主机的内存信息
    meminfo_content = fetch_meminfo(conn)

    # 解析交换空间信息
    swap_info = parse_swapinfo(meminfo_content)

    # 计算交换空间使用率
    usage_rate = swap_usage(swap_info)

    # 输出交换空间使用率
    print(f"Swap Usage: {usage_rate:.2f}%")
    return usage_rate


