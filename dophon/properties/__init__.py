# coding: utf-8"
import sys
"""
配置集合
author:CallMeE
date:2018-06-01
"""

print('引用默认配置')
# 此处为服务器配置
host = '127.0.0.1'
port = 443
ssl_context = 'adhoc'

# 此处为蓝图文件夹配置
blueprint_path = ['/routes_package_path']
pool_conn_num = 'db_connect_pool_size'

# 此处为数据库配置
pydc_host = 'localhost'
pydc_port = 3306
pydc_user = 'username'
pydc_password = 'password'
pydc_database = 'database'


def get_properties(prop_path=None):
    if prop_path:
        sys.modules['properties']=__import__(prop_path,fromlist=True)