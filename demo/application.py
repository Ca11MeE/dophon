# coding: utf-8"
import os
"""
配置集合
author:CallMeE
date:2018-06-01
"""
project_root=os.getcwd()

# 此处为服务器配置
host='0.0.0.0'
port=443
ssl_context=('./ssl/1_274698001.zxyzt.cn_bundle.crt','./ssl/2_274698001.zxyzt.cn.key')

# 此处为蓝图文件夹配置
blueprint_path = ['/routes']
pool_conn_num=5

# 此处为数据库配置
# pydc_host = 'bdm238721578.my3w.com'
# pydc_user = 'bdm238721578'
# pydc_password = 'ealohu31841'
# pydc_database = 'bdm238721578_db'
pydc_host = 'cdb-nzo3mn4f.gz.tencentcdb.com'
pydc_port=10005
pydc_user = 'root'
pydc_password = 'ealohu31841'
pydc_database = 'agymall_db'

