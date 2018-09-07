# coding: utf-8"
import os

"""
配置集合
author:CallMeE
date:2018-06-01
"""
project_root = os.getcwd()

server_gevented = True

debug_trace = True

ip_count = True

# 此处为服务器配置
host = '0.0.0.0'
port = 80
ssl_context = 'adhoc'

# 此处为路由文件夹配置
blueprint_path = ['/routes']
pool_conn_num = 5

# 此处为数据库配置
# pydc_host = 'bdm238721578.my3w.com'
# pydc_user = 'bdm238721578'
# pydc_password = 'ealohu31841'
# pydc_database = 'bdm238721578_db'
pydc_host = 'localhost'
pydc_port = 3306
pydc_user = 'root'
pydc_password = 'wo4ce4kumima'
pydc_database = 'mw2017_db'

# 此处为日志配置
logger_config = {
    # 'filename': 'app.log',
    # 'level': 'logging.DEBUG',
    'format': '%(levelname)s : <%(module)s> (%(asctime)s) ==> %(filename)s {%(funcName)s} [line:%(lineno)d] ::: %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S'
}
