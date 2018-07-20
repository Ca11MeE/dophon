# coding: utf-8"
import sys
import os

"""
配置集合
author:CallMeE
date:2018-06-01
"""

project_root = os.getcwd()

# 此处为服务器配置
host = '127.0.0.1'
port = 443
ssl_context = 'adhoc'

# 此处为蓝图文件夹配置
blueprint_path = ['/routes']  # route model dir path
pool_conn_num = 5  # size of db connect pool

# 此处为数据库配置
pydc_host = 'localhost'
pydc_port = 3306
pydc_user = 'root'
pydc_password = 'root'
pydc_database = 'zxyzt'

# 此处为日志配置
logger_config={
    # 'filename': 'app.log',
    # 'level': 'logging.DEBUG',
    'format': '%(levelname)s : <%(module)s> (%(asctime)s) ==> %(filename)s {%(funcName)s} [line:%(lineno)d] ::: %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S'
}


def get_properties(prop_path=None):
    if prop_path:
        sys.modules['properties'] = __import__(prop_path, fromlist=True)

