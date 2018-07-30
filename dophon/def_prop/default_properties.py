# coding: utf-8"
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

