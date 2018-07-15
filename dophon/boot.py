# coding: utf-8

"""
配置管理
启动前尝试获得自定义配置(application.py)
无法获取则使用默认配置
"""
import sys


def read_self_prop():
    sys.modules['properties'] = __import__('application', fromlist=True)
    sys.modules['dophon.properties'] = __import__('application', fromlist=True)


try:
    read_self_prop()
except Exception as e:
    sys.stdout.write('没有找到自定义配置:(application.py)')
    sys.stdout.flush()

from flask import Flask, Blueprint
import os, re
from dophon import mysql
from dophon.mysql import Pool
from dophon import properties

app_name = properties.service_name if hasattr(properties, 'service_name') else __name__
# 定义WEB容器(同时防止json以ascii解码返回)
app = Flask(app_name)
app.config['JSON_AS_ASCII'] = False


# 处理各模块中的自动注入以及组装各蓝图
# dir_path中为蓝图模块路径,例如需要引入的蓝图都在routes文件夹中,则传入参数'/routes'
def map_apps(dir_path):
    path = os.getcwd() + dir_path
    if not os.path.exists(path):
        sys.stderr.write('蓝图文件夹不存在,创建蓝图文件夹')
        sys.stderr.flush()
        os.mkdir(path)
    list = os.listdir(path)
    print('蓝图文件夹:', '.', dir_path)
    # list.remove('__pycache__')
    while list:
        try:
            file = list.pop(0)
            if file.startswith('__') and file.endswith('__'):
                continue
            i = os.path.join(path, file)
            if os.path.isdir(i):
                continue
            print('加载蓝图模块:', file)
            f_model = __import__(re.sub('/', '', dir_path) + '.' + re.sub('\.py', '', file), fromlist=True)
            app.register_blueprint(f_model.app)
        except Exception as e:
            raise e
            pass


def get_app():
    return app


def run_app(host=properties.host, port=properties.port):
    app.run(host=host, port=port)


def run_app_ssl(host=properties.host, port=properties.port, ssl_context=properties.ssl_context):
    app.run(host=host, port=port, ssl_context=ssl_context)


def bootstrap_app():
    global app
    b = __import__('flask_bootstrap')
    b.Bootstrap(app)


print('加载数据库模块')
mysql.pool = Pool.Pool()
# print('加载完毕')

print('蓝图初始化')
for path in properties.blueprint_path:
    map_apps(path)
