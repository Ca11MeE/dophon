# coding: utf-8

"""
配置管理
启动前尝试获得自定义配置(application.py)
无法获取则使用默认配置
"""
import ctypes
import inspect
import sys
import logging
import os, re


def read_self_prop():
    try:
        def_prop = __import__('dophon.def_prop.default_properties', fromlist=True)
        u_prop = __import__('application', fromlist=True)
        # 对比配置文件
        for name in dir(def_prop):
            if re.match('__.*__', name):
                continue
            if name in dir(u_prop):
                continue
            setattr(u_prop, name, getattr(def_prop, name))
        sys.modules['properties'] = u_prop
        sys.modules['dophon.properties'] = u_prop
    except Exception as e:
        logging.error(e)
        sys.modules['properties'] = def_prop
        sys.modules['dophon.properties'] = def_prop


try:
    read_self_prop()
except Exception as e:
    logging.error('没有找到自定义配置:(application.py)')
    logging.error('引用默认配置')

from dophon import logger

logger.inject_logger(globals())

from flask import Flask
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
        logger.error('蓝图文件夹不存在,创建蓝图文件夹')
        os.mkdir(path)
    f_list = os.listdir(path)
    logger.info('蓝图文件夹: %s', dir_path)
    while f_list:
        try:
            file = f_list.pop(0)
            if re.match('__.*__', file):
                continue
            i = os.path.join(path, file)
            if os.path.isdir(i):
                logger.info('加载蓝图模块: %s', file)
                continue
            f_model = __import__(re.sub('/', '', dir_path) + '.' + re.sub('\.py', '', file), fromlist=True)
            app.register_blueprint(f_model.app)
        except Exception as e:
            raise e
            pass


logger.info('加载数据库模块')
connection_pool = mysql.pool = Pool.Pool()
# print('加载完毕')

logger.info('蓝图初始化')
for path in properties.blueprint_path:
    map_apps(path)


def get_app() -> Flask:
    return app


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


def free_source():
    def method(f):
        def args(*arg, **kwarg):
            logger.info('启动服务器')
            f(*arg, **kwarg)
            """
            释放所有资源
            :return:
            """
            logger.info('服务器关闭')
            logger.info('释放资源')
            # 释放连接池资源
            connection_pool.free_pool()
            logger.info('释放连接池')
            logger.info('再次按下Ctrl+C退出')

        return args

    return method


@free_source()
def run_app(host=properties.host, port=properties.port):
    # 开启多线程处理
    app.run(host=host, port=port, threaded=True)


@free_source()
def run_app_ssl(host=properties.host, port=properties.port, ssl_context=properties.ssl_context):
    # 开启多线程处理
    app.run(host=host, port=port, ssl_context=ssl_context, threaded=True)


def bootstrap_app():
    """
    bootstrap样式页面初始化
    :return:
    """
    global app
    b = __import__('flask_bootstrap')
    b.Bootstrap(app)


def run_as_docker():
    """
    利用docker启动项目
    :return:
    """
    logger.info('容器前期准备')
    root = re.sub('\\\\', '/', properties.project_root)
    import platform
    p_version = platform.python_version()
    work_dir = './' + os.path.basename(root)
    port = properties.port
    port_str = str(port)
    # 生成依赖文件
    logger.info('生成依赖文件')
    os.system('pip freeze >pre_requirements.txt')
    with open('./pre_requirements.txt', 'r') as file:
        with open('./requirements.txt', 'w') as final_file:
            for line in file.readlines():
                for key in sys.modules.keys():
                    if re.search('(_|__|\\.).+$', key):
                        continue
                    module_path = re.sub('(>=|==|=>|<=|=<|<|>|=).*\s+', '', line.lower())
                    if re.search(module_path, key.lower()):
                        final_file.write(line)
                        continue
    # 生成Dockerfile
    logger.info('生成Dockerfile')
    with open('./Dockerfile', 'w') as file:
        file.write('FROM python:' + p_version + '\n')
        file.write('ADD . ' + work_dir + '\n')
        file.write('WORKDIR ' + work_dir + '\n')
        file.write('RUN pip install -r requirements.txt' + '\n')
        file.write('CMD ["python","' + work_dir + '/Bootstrap.py"]' + '\n')
    os.system('cd '+ root)
    logger.info('移除旧镜像')
    os.system('docker rmi '+os.path.basename(root))
    logger.info('建立镜像')
    os.system('docker build -t ' + os.path.basename(root) + ' .')
    logger.info('运行镜像')
    os.system(
        'docker run -p ' + port_str + ':' + port_str + ' -d --name ' + os.path.basename(root) + ' ' + os.path.basename(
            root))
