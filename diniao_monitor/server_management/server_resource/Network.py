# @Time    : 2024/8/28 15:08
# @Author  :      
import time
import re
from fabric import Connection
from fabric import task


def parse_netdev(content):
    """解析 /proc/net/dev 文件中的网络统计信息"""
    net_info = {}
    lines = content.splitlines()
    for line in lines[2:]:  # Skip header lines
        fields = line.split()
        iface = fields[0].strip(':')
        rx_bytes = int(fields[1])
        tx_bytes = int(fields[9])
        net_info[iface] = {'rx_bytes': rx_bytes, 'tx_bytes': tx_bytes}
    return net_info


def calculate_rate(start_data, end_data, interval):
    """计算网络输入输出速率"""
    rates = {}
    for iface in start_data:
        if iface in end_data:
            rx_rate = (end_data[iface]['rx_bytes'] - start_data[iface]['rx_bytes']) / interval
            tx_rate = (end_data[iface]['tx_bytes'] - start_data[iface]['tx_bytes']) / interval
            rates[iface] = {'rx_rate': rx_rate, 'tx_rate': tx_rate}
    return rates


@task
def fetch_netdev(c):
    """从远程主机获取 /proc/net/dev 文件内容"""
    result = c.run('cat /proc/net/dev', hide=True)
    return result.stdout


def run_network(host, user, connect_kwargs, port):
    # 连接到远程主机
    conn = Connection(host=host, user=user, port=port, connect_kwargs={"password": connect_kwargs})

    # 获取初始网络统计数据
    netdev_content_start = fetch_netdev(conn)
    netdev_data_start = parse_netdev(netdev_content_start)

    # 等待一段时间，例如 1 秒钟
    time.sleep(1)

    # 获取终止网络统计数据
    netdev_content_end = fetch_netdev(conn)
    netdev_data_end = parse_netdev(netdev_content_end)

    # 计算网络输入输出速率
    rates = calculate_rate(netdev_data_start, netdev_data_end, 1)

    # 输出网络速率
    for iface, rate in rates.items():
        print(f"Interface: {iface}")
        print(f"  RX Rate: {rate['rx_rate'] / 1024:.2f} KB/s")
        print(f"  TX Rate: {rate['tx_rate'] / 1024:.2f} KB/s")

    return rates
