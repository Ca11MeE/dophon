# coding: utf-8"
import os

"""
配置集合
author:CallMeE
date:2018-06-01
"""

project_root = os.getcwd()

# 服务器相关配置
server_threaded = False  # 服务器多线程开关
server_gevented = False  # 服务器gevent协程处理(会覆盖多线程开关)

debug_trace = False  # 调试跟踪记录

# 此为开启ip防火墙模式(1秒不超过50次请求,60秒解冻)
ip_count = False

# 此处为服务器配置
host = '127.0.0.1'
port = 443
ssl_context = 'adhoc'

# 此处为路由文件夹配置
blueprint_path = ['/routes']  # route model dir path
pool_conn_num = 5  # size of db connect pool

# 此处为数据库配置
pydc_host = 'localhost'
pydc_port = 3306
pydc_user = 'root'
pydc_password = 'root'
pydc_database = 'db'
pydc_xmlupdate_sech = False

# 消息队列线程池工人数
msg_queue_max_num = 30

# 此处为日志配置
logger_config = {
    # 'filename': 'app.log',
    # 'level': 'logging.DEBUG',
    'format': '%(levelname)s : <%(module)s> (%(asctime)s) ==> %(filename)s {%(funcName)s} [line:%(lineno)d] ::: %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S'
}
