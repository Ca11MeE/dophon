# coding: utf-8
from flask import Flask
import dophon.mysql as mysql, os, re
from dophon.mysql import Pool
import dophon.properties as properties

# 定义WEB容器(同时防止json以ascii解码返回)
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


# 处理各模块中的自动注入以及组装各蓝图
# dir_path中为蓝图模块路径,例如需要引入的蓝图都在routes文件夹中,则传入参数'/routes'
def map_apps(dir_path):
    path = os.getcwd() + dir_path
    list = os.listdir(path)
    print('蓝图文件夹:', '.', dir_path)
    while list:
        try:
            file = list.pop(0)
            if file.startswith('__') and file.endswith('__'):
                continue
            print('加载蓝图模块:', file)
            f_model = __import__(re.sub('/', '', dir_path) + '.' + re.sub('\.py', '', file), fromlist=True)
            app.register_blueprint(f_model.app)
        except:
            pass


def get_app():
    return app


def run_app(host=properties.host, port=properties.port):
    app.run(host=host, port=port)


def run_app_ssl(host=properties.host, port=properties.port, ssl_context=properties.ssl_context):
    app.run(host=host, port=port, ssl_context=ssl_context)


print('加载数据库模块')
mysql.pool = Pool.Pool()

print('蓝图初始化')
for path in properties.blueprint_path:
    map_apps(path)
