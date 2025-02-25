import json
from django.http import JsonResponse
from fabric import Connection
from fabric import task
import time


def parse_cpu_line(line):
    """解析以 cpu 开头的行"""
    parts = line.split()
    return {
        'cpu': parts[0],
        'user': int(parts[1]),
        'nice': int(parts[2]),
        'system': int(parts[3]),
        'idle': int(parts[4]),
        'iowait': int(parts[5]),
        'irq': int(parts[6]),
        'softirq': int(parts[7]),
        'steal': int(parts[8]),
        'guest': int(parts[9]),
        'guest_nice': int(parts[10])
    }


def calculate_cpu_usage(cpu_data_t0, cpu_data_t1):
    """计算 CPU 使用率"""
    allbasytime_t0 = cpu_data_t0['user'] + cpu_data_t0['nice'] + cpu_data_t0['system'] + cpu_data_t0['irq'] + \
                     cpu_data_t0['softirq']
    allruntime_t0 = allbasytime_t0 + cpu_data_t0['idle'] + cpu_data_t0['iowait'] + cpu_data_t0['steal'] + cpu_data_t0[
        'guest']

    allbasytime_t1 = cpu_data_t1['user'] + cpu_data_t1['nice'] + cpu_data_t1['system'] + cpu_data_t1['irq'] + \
                     cpu_data_t1['softirq']
    allruntime_t1 = allbasytime_t1 + cpu_data_t1['idle'] + cpu_data_t1['iowait'] + cpu_data_t1['steal'] + cpu_data_t1[
        'guest']

    userate = (allbasytime_t1 - allbasytime_t0) / (allruntime_t1 - allruntime_t0) * 100.0
    return userate


@task
def fetch_stat(c):
    """从远程主机获取 /proc/stat 文件内容"""
    result = c.run('cat /proc/stat', hide=True)
    return result.stdout


def run_cpu(host, user, connect_kwargs, port):
    # 连接到远程主机
    conn = Connection(host=host, user=user, port=port, connect_kwargs={"password": connect_kwargs})

    # 获取第一次采样数据
    content_t0 = fetch_stat(conn)
    time.sleep(1)  # 等待 1 秒钟再进行第二次采样

    # 获取第二次采样数据
    content_t1 = fetch_stat(conn)

    # 解析数据
    cpu_lines_t0 = {}
    cpu_lines_t1 = {}

    for line in content_t0.splitlines():
        if line.startswith('cpu'):
            cpu_line = parse_cpu_line(line)
            cpu_lines_t0[cpu_line['cpu']] = cpu_line

    for line in content_t1.splitlines():
        if line.startswith('cpu'):
            cpu_line = parse_cpu_line(line)
            cpu_lines_t1[cpu_line['cpu']] = cpu_line

    # 计算每个 CPU 核心的使用率
    cpu_usage = {}

    total_usage = 0  # 用于计算所有核心的平均使用率
    core_count = 0  # 核心数目


    for cpu_key in cpu_lines_t0:
        if cpu_key in cpu_lines_t1:
            cpu_data_t0 = cpu_lines_t0[cpu_key]
            cpu_data_t1 = cpu_lines_t1[cpu_key]
            usage = calculate_cpu_usage(cpu_data_t0, cpu_data_t1)
            cpu_usage[cpu_key] = f'{usage:.2f}%'
            
            total_usage += usage
            core_count += 1
        else:
            cpu_usage[cpu_key] = '数据不完整'

    # 计算平均使用率
    if core_count > 0:
        average_usage = total_usage / core_count
    else:
        average_usage = 0.0

    # # 将结果转换为 JSON 格式
    # json_output = json.dumps(cpu_usage, indent=4, ensure_ascii=False)
    # # 打印 JSON 格式的输出
    # print(json_output)
    print(f"CPU平均使用率: {average_usage:.2f}%")
    # return json_output
    return average_usage
