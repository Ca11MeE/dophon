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
import os, re, json
from datetime import datetime
from threading import *


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

from flask import Flask, request,abort
from dophon import mysql
from dophon.mysql import Pool
from dophon import properties

app_name = properties.service_name if hasattr(properties, 'service_name') else __name__
# 定义WEB容器(同时防止json以ascii解码返回)
app = Flask(app_name)
app.config['JSON_AS_ASCII'] = False

# ip计数缓存
ip_count = {}
ipcount_lock = Lock()
if os.path.exists(os.getcwd()+'/ip_count'):
    with open('ip_count', 'r') as ip_count_file:
        file_text = ip_count_file.read()
        if file_text:
            ip_count = eval(file_text)
else:
    with open('ip_count', 'w') as ip_count_file:
        json.dump({},ip_count_file)

# IP黑名单
ip_refuse_list = {}


def before_request():
    """
    定义拦截器
    :return:
    """
    ipcount_lock.locked()
    ip = request.remote_addr
    now_timestemp = datetime.now().timestamp()
    # 检测是否为黑名单
    if ip in ip_refuse_list:
        # 默认禁用一分钟
        if (int(now_timestemp) - int(ip_refuse_list[ip])) > 60:
            # 可以清除白名单
            ip_refuse_list.pop(ip)
            # 清除访问记录
            ip_count[ip]['req_timestemp']=[now_timestemp]
        else:
            # 未到解禁时间
            return abort(400)
    if ip in ip_count:
        ip_item = ip_count[ip]
        ip_item['req_count'] += 1
        req_timestemp = ip_item['req_timestemp']
        '''
        判断逻辑:
            当前请求时间是最近的,连续的1秒内
        '''
        if (int(now_timestemp) - int(req_timestemp[0])) > 1 \
                and \
                (int(now_timestemp) - int(req_timestemp[len(req_timestemp)-1])) < 1:
            # 检测3秒内请求数
            if len(req_timestemp) > 50:
                # 默认三秒内请求不超过300
                # 超出策略则添加到黑名单
                ip_refuse_list[ip]=now_timestemp
            else:
                # 不超出策略则清空请求时间戳缓存
                ip_item['req_timestemp'] = [now_timestemp]
        else:
            ip_item['req_timestemp'].append(now_timestemp)
    else:
        ip_item = {
            'req_count': 1,
            'req_timestemp': [now_timestemp]
        }
    Thread(target=persist_ip_count).start()
    ip_count[ip] = ip_item


def persist_ip_count():
    """
    持久化ip统计到文件
    :return:
    """
    # 持久化ip统计
    with open('ip_count', 'w') as ip_count_file:
        json.dump(ip_count, ip_count_file)
    if ipcount_lock.locked():
        ipcount_lock.release()


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
            filter_method = f_model.app.before_request(before_request)
            if hasattr(properties, 'ip_count') and getattr(properties, 'ip_count'):
                setattr(f_model, 'before_request', filter_method)
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


def fix_static(
        fix_target: Flask = app,
        static_floder: str = 'static'
):
    """
    修正静态文件路径
    :return:
    """
    if hasattr(fix_target, 'static_folder'):
        if hasattr(properties, 'project_root'):
            root_path = properties.project_root
        else:
            root_path = os.getcwd()
        fix_target.static_folder = root_path + '/' + static_floder
    else:
        raise Exception('错误的修复对象')


def fix_template(
        fix_target: Flask = app,
        template_folder: str = 'templates'
):
    """
    修正页面模板文件路径
    :return:
    """
    if hasattr(fix_target, 'template_folder'):
        if hasattr(properties, 'project_root'):
            root_path = properties.project_root
        else:
            root_path = os.getcwd()
        fix_target.template_folder = root_path + '/' + template_folder
    else:
        raise Exception('错误的修复对象')


@free_source()
def run_app(host=properties.host, port=properties.port):
    # 开启多线程处理
    app.run(host=host, port=port, threaded=True)


@free_source()
def run_app_ssl(host=properties.host, port=properties.port, ssl_context=properties.ssl_context):
    # 开启多线程处理
    app.run(host=host, port=port, ssl_context=ssl_context, threaded=True)


from dophon.annotation import *


@RequestMapping(app, '/framework/ip/count', ['get', 'post'])
@ResponseBody()
def view_ip_count():
    """
    此为公共请求,不计入ip统计
    :return:
    """
    return ip_count


@RequestMapping(app, '/framework/ip/refuse', ['get', 'post'])
@ResponseBody()
def view_ip_refuse():
    """
    此为公共请求,不计入ip统计
    :return:
    """
    return ip_refuse_list


def bootstrap_app():
    """
    bootstrap样式页面初始化
    :return:
    """
    global app
    b = __import__('flask_bootstrap')
    b.Bootstrap(app)
