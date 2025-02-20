# @Time    : 2025/2/13 20:55
# @Author  :      
global_server_data = {}


# 更新服务器数据的函数
def update_server_data(server_id, data):
    global global_server_data
    global_server_data[server_id] = data


# 获取服务器数据的函数
def get_server_data(server_id):
    return global_server_data.get(server_id)
