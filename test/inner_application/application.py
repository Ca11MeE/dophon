host = '127.0.0.1'
port = 18080
server_processes = 3
blueprint_path = ['/routes']
mq = {'remote_center': False}

# 远程配置
# remote_prop = {
#     'base': '127.0.0.1:833', # 根路径
#     'mark': ['config','get'], # 配置标识
#     # 'method':'post' # 获取方法
# }
