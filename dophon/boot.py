# coding: utf-8
import traceback
import functools
import os
import sys
import re
from datetime import datetime
from threading import *
import json

from dophon import pre_boot
from dophon_logger import *

logger = get_logger(DOPHON)

logger.inject_logger(globals())

pre_boot.check_modules()

from flask import Flask, request, abort, jsonify
from dophon import properties, blue_print
from html import escape
from dophon.tools import gc
from . import tools
from .tools.dynamic_import import d_import

# 旧版本与数据库的耦合,后期版本移除
try:
    mysql = __import__('dophon.db.mysql')
except:
    mysql = None


def load_banner():
    """
    加载header-banner文件
    :return:
    """
    file_root = properties.project_root
    file_path = file_root + os.path.sep + 'header.txt'
    if os.path.exists(file_path):
        with open(file_path, encoding='utf8') as banner:
            for line in banner.readlines():
                sys.stdout.write(line)
    else:
        tools.show_banner()
    sys.stdout.flush()


def load_footer():
    """
    加载footer-banner文件
    :return:
    """
    file_root = properties.project_root
    file_path = file_root + os.path.sep + 'footer.txt'
    if os.path.exists(file_path):
        with open(file_path, encoding='utf8') as banner:
            for line in banner.readlines():
                sys.stdout.write(line)
    sys.stdout.flush()


error_info = properties.error_info


def boot_init():
    """
    初始化启动
    :return:
    """
    global app_name, app, ip_count, ipcount_lock, ip_refuse_list
    load_banner()
    app_name = properties.service_name if hasattr(properties, 'service_name') else __name__
    # 定义WEB容器(同时防止json以ascii解码返回)
    app = Flask(app_name)
    app.config['JSON_AS_ASCII'] = False

    # ip计数缓存
    ip_count = {}
    ipcount_lock = Lock()
    if os.path.exists(os.getcwd() + '/ip_count'):
        with open('ip_count', 'r') as ip_count_file:
            file_text = ip_count_file.read()
            if file_text:
                ip_count = eval(file_text)
    else:
        with open('ip_count', 'w') as ip_count_file:
            json.dump({}, ip_count_file)
    # IP黑名单
    ip_refuse_list = {}


boot_init()


def before_request():
    """
    定义拦截器
    :return:
    """
    if properties.ip_count:
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
                ip_count[ip]['req_timestemp'] = [now_timestemp]
            else:
                # 未到解禁时间
                return abort(400)
        if ip in ip_count:
            ip_item = ip_count[ip]
            ip_item['req_count'] += 1
            req_timestemp = ip_item['req_timestemp']
            """
            判断逻辑:
                当前请求时间是最近的,连续的1秒内
            """
            if (int(now_timestemp) - int(req_timestemp[0])) > 1 \
                    and \
                            (int(now_timestemp) - int(req_timestemp[len(req_timestemp) - 1])) < 1:
                # 检测3秒内请求数
                if len(req_timestemp) > 50:
                    # 默认三秒内请求不超过300
                    # 超出策略则添加到黑名单
                    ip_refuse_list[ip] = now_timestemp
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


blueprint_init_queue = {}  # 蓝图初始化方法缓存(用于初始化后启动)


# 处理各模块中的自动注入以及组装各路由
# dir_path中为路由模块路径,例如需要引入的路由都在routes文件夹中,则传入参数'/routes'
def map_apps(dir_path):
    path = os.getcwd() + dir_path
    if not os.path.exists(path):
        logger.error('路由文件夹不存在,创建路由文件夹')
        os.mkdir(path)
    f_list = os.listdir(path)
    logger.info(f'路由文件夹: {dir_path}')
    while f_list:
        try:
            file = f_list.pop(0)
            if re.match('__.*__', file):
                continue
            i = os.path.join(path, file)
            if os.path.isdir(i):
                logger.info(f'加载路由模块: {file}')
                # 扫描内部文件夹
                map_apps(f'{dir_path}{os.sep}{file}')
                continue
            file_name = re.sub('\.py', '', file)
            module_path = re.sub('^\.', '', re.sub('\\\\|/', '.', dir_path))
            # print(module_path)
            f_model = __import__(f'{module_path}.{file_name}', fromlist=True)

            # 自动装配蓝图实例并自动配置部分参数,免除繁琐配置以及精简代码
            package_app = getattr(f_model, '__app') \
                if hasattr(f_model, '__app') \
                else f_model.app \
                if hasattr(f_model, 'app') \
                else blue_print(f"_boot_auto_reg.{file_name}", getattr(f_model, '__name__'))
            filter_method = package_app.before_request(before_request)
            # 若需统计请求,装配请求统计方法
            if hasattr(properties, 'ip_count') and getattr(properties, 'ip_count'):
                setattr(f_model, 'before_request', filter_method)
            # 若存在初始化执行方法,执行该方法
            if hasattr(f_model, 'blueprint_init'):
                init_fun = getattr(f_model, 'blueprint_init')
                # 判断是否方法
                if callable(init_fun):
                    blueprint_init_queue[f_model] = before_bp_init_fun(init_fun)
            get_app().register_blueprint(package_app)

        except Exception as e:
            raise e
            pass

            # for name in dir(item):
            #     print(f'{name} ==> {getattr(item, name)}')

            # print(get_app().blueprints)


def BeanScan(scan_path: list = []):
    def method(f):
        def method_args(*args, **kwargs):
            logger.debug('mapping beans')
            for bean_path in scan_path if scan_path else properties.components_path:
                is_project_root = os.path.abspath(properties.project_root + bean_path) == os.path.abspath(
                    properties.project_root)
                if is_project_root:
                    # 若配置项目自身路径则提示警告
                    logger.warning(f'扫描路径(components_path)存在项目根路径的配置会导致项目异常启动,请注意')
                map_bean(bean_path)
            return f(*args, **kwargs)

        return method_args

    return method


def map_bean(bean_path: str, is_project_root: bool = False):
    __project_root = properties.project_root.replace("\\", "/")
    bean_dir = re.sub('(\\\\|/)', '', bean_path)
    # 不存在路由定义
    # print(f'bean_path: {bean_path}')
    try:
        for root, dirs, files in os.walk(f'{__project_root}{bean_path}'):
            relative_path = re.sub(f'{__project_root}', '', root)
            # 若处于路由定义则跳过
            # 相对路径为根路径也跳过
            # 强制指定为项目根路径也跳过
            if relative_path in properties.blueprint_path \
                    or relative_path == '/' \
                    or relative_path.endswith('__') \
                    or is_project_root:
                continue
            logger.debug(f'scan path {relative_path}')
            # exec(f'from {re.sub("/", ".", __bean_dir)} import {module_path.split(".")[-1]}')
            # print(f'{relative_path} => {dirs} => {files}')
            for file in files:
                file_short_name = os.path.basename(file).split(".")[0]
                if not file.endswith('.py') or re.match('__.+__', file_short_name):
                    # 不是python脚本文件
                    continue
                # 获取内部文件路径
                __file_path = f'{relative_path}/{file_short_name}'
                # 整理成包形式
                __file_package = re.sub('(\\\\|/)', '.', __file_path)
                # print(__file_package)
                __file_package_part = __file_package.split('.')[1:]
                # print(__file_package_part)
                __exec_code = f'from {".".join(__file_package_part[:-1])} import {__file_package_part[-1]}'
                # print(__exec_code)
                logger.debug(f'mapping bean {__file_package_part[-1]} {__exec_code}')
                exec(__exec_code)
        __import__(bean_dir, fromlist=bean_dir)
    except Exception as e:
        pass


def before_bp_init_fun(f):
    """
    预留蓝图初始化装饰器
    :param f:
    :return:
    """

    # print(f)

    def fields(*args, **kwargs):
        # print('args: ', args, 'kwargs:', kwargs)
        f(*args, **kwargs)

    return fields


def get_app() -> Flask:
    return app


def free_source():
    def method(f):
        @functools.wraps(f)
        def args(*arg, **kwarg):
            try:
                logger.info('启动服务器')
                logger.info('路由初始化')
                logger.debug('mapping routes')
                for path in properties.blueprint_path:
                    map_apps(path)
                load_footer()
                # 执行蓝图初始化方法
                for blueprint_module, blue_print_init_method in blueprint_init_queue.items():
                    try:
                        blue_print_init_method()
                    except Exception as e:
                        logger.error(f'蓝图"{blueprint_module}"初始化失败,信息: {e}')
                # for rule in get_app().url_map.iter_rules():
                #     print(str(rule))
                # print(rule.get_rules())
                # for name in dir(rule):
                #     print(f'{name}---{getattr(rule,name)}')
                # print(help(rule))
                # break
                f(*arg, **kwarg)
                """
                释放所有资源
                :return:
                """
                logger.info('服务器关闭')
                logger.debug('释放资源')
                if mysql:
                    mysql.free_pool()
                logger.debug('释放连接池')
                sys.exit()
                # logger.info('再次按下Ctrl+C退出')
            except Exception as e:
                logger.error(e)

        return args

    return method


def fix_static(
        fix_target: Flask = app,
        static_floder: str = 'static',
        enhance_power: bool = False
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
        static_floder_path = root_path + '/' + static_floder
        fix_target.static_folder = static_floder_path
        if os.path.exists(static_floder_path) and enhance_power:
            enhance_static_route(static_floder_path)
    else:
        raise Exception('错误的修复对象')


def enhance_static_route(static_floder_path: str):
    """
    增强静态文件路由能力
    :param static_floder_path:
    :param serlize:
    :return:
    """
    framework_static_route_path = f'{properties.project_root}{properties.blueprint_path[0]}/FrameworkStaticRoute.py'
    # if not os.path.exists(framework_static_route_path):
    linux_static_floder_path = static_floder_path.replace('\\', '/')
    if True:
        # import types
        import uuid
        # 定义静态资源获取路径
        logger.info('增强静态文件路由')
        with open(framework_static_route_path, 'wb') as fsroute:
            # 写入预设信息
            fsroute.write(bytes(
                f"# -*- coding: utf-8 -*-\n"
                f"from dophon import blue_print\n"
                f"from dophon.annotation import *\n"
                f"from flask import url_for\n"
                f"from flask import render_template\n"
                f"from flask import send_from_directory\n"
                f"app = blue_print('FrameworkStaticRoute', __name__,static_folder='{linux_static_floder_path}')\n",
                encoding='utf-8'))
            for root, dir_path, file in os.walk(linux_static_floder_path):
                # 消除转义字符(win)
                root = re.sub('\\\\', '/', root)
                linux_static_floder_path = re.sub('\\\\', '/', linux_static_floder_path)
                # 静态目录下的目录名
                root_dir_path = re.sub('\\\\', '/', re.sub(linux_static_floder_path, "", root))
                # 解析静态资源路径
                route_name = re.sub('[^(1-9a-zA-Z_)]', '',
                                    f'{re.sub(static_floder_path, "", root)}_{root_dir_path}_{uuid.uuid1()}')
                route_path = f'{root_dir_path}/<file_name>'
                static_url_method_code_body = \
                    f"@RequestMapping('{route_path}',['get','post'])\ndef {route_name}(file_name):\n\t" \
                    f"\"\"\"\n\t" \
                    f"static file route in {route_path}\n\t" \
                    f":param file_name: static file name\n\t" \
                    f":return static file blob\n\t" \
                    f"\"\"\"\n\t" \
                    f"return render_template(f'{root_dir_path}/" \
                    "{file_name}" \
                    f"') if file_name.endswith('.html') " \
                    f"else send_from_directory('{linux_static_floder_path}{root_dir_path}',f" \
                    "'{file_name}'" \
                    ",as_attachment=True)\n"
                fsroute.write(bytes(
                    static_url_method_code_body,
                    encoding='utf-8'))
        logger.info("增强静态文件夹完毕")


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
    logger.info(f'监听地址: {host} : {port}')
    if properties.server_threaded:
        # 开启多线程处理
        app.run(host=host, port=port, threaded=properties.server_threaded)
    elif tools.is_not_windows() and properties.server_processes > 1:
        # 开启多进程处理
        print('开启多进程', properties.server_processes)
        app.run(host=host, port=port, threaded=False, processes=properties.server_processes)
    else:
        app.run(host=host, port=port)


@free_source()
def tornado(host=properties.host, port=properties.port):
    logger.info(f'添加Tornado核心')
    d_import('tornado')
    from tornado.wsgi import WSGIContainer
    from tornado.httpserver import HTTPServer
    from tornado.ioloop import IOLoop
    logger.info(f'开始使用Tornado增强')
    http_server = HTTPServer(WSGIContainer(get_app()))
    logger.info(f'监听{port}')
    if tools.is_not_windows() and properties.server_processes > 1:
        http_server.bind(port, host)  # flask默认的端口
        http_server.start(properties.server_processes)
    else:
        http_server.listen(port, host)  # flask默认的端口
    logger.info(f'监听地址: {host}:{port}')
    IOLoop.current().start()


@free_source()
def run_app_ssl(host=properties.host, port=properties.port, ssl_context=properties.ssl_context):
    logger.info(f'监听地址: {host} : {port}')
    if properties.server_threaded:
        # 开启多线程处理
        app.run(host=host, port=port, ssl_context=ssl_context, threaded=properties.server_threaded)
    elif tools.is_not_windows() and properties.server_processes > 1:
        # 开启多进程处理
        app.run(host=host, port=port, ssl_context=ssl_context, threaded=False,
                processes=properties.server_processes)
    else:
        app.run(host=host, port=port, ssl_context=ssl_context)


@free_source()
def tornado_ssl(host=properties.host, port=properties.port, ssl_context=properties.ssl_context):
    logger.info(f'添加Tornado核心')
    from tornado.wsgi import WSGIContainer
    from tornado.httpserver import HTTPServer
    from tornado.ioloop import IOLoop
    logger.info(f'开始使用Tornado增强')
    http_server = HTTPServer(WSGIContainer(get_app()), ssl_options={
        'certfile': ssl_context[0],
        'keyfile': ssl_context[1],
    })
    logger.info(f'监听{port}')
    if tools.is_not_windows() and properties.server_processes > 1:
        http_server.bind(port)  # flask默认的端口
        http_server.start(properties.server_processes)
    else:
        http_server.listen(port)  # flask默认的端口
    logger.info(f'监听地址: {host}:{port}')
    IOLoop.current().start()


def run_f(ssl: bool = False, **kwargs):
    """
    flask 启动入口
    :param ssl:
    :param kwargs:
    :return:
    """
    run_app_ssl(**kwargs) if ssl else run_app(**kwargs)


def run_t(ssl: bool = False, **kwargs):
    """
    tornado 启动入口
    :param ssl:
    :param kwargs:
    :return:
    """
    tornado_ssl(**kwargs) if ssl else tornado(**kwargs)


FLASK = 0
TORNADO = 1


def run(run_type: int = FLASK, ssl: bool = False, **kwargs):
    """
    统一入口
    :param run_type: 启动类型
    :param ssl:  https开关
    :param kwargs: 启动参数
    :return:
    """
    run_f(ssl, **kwargs) if run_type == FLASK else run_t(ssl, **kwargs) if run_type == TORNADO else 1 / 0


def bootstrap_app():
    """
    bootstrap样式页面初始化
    :return:
    """
    global app
    b = __import__('flask_bootstrap')
    b.Bootstrap(app)


from dophon.annotation import *


# region 定义内部接口

@GetRoute('/find/function/desc/by/module/<module_path>')
@ResponseBody()
def find_function_desc_by_module(module_path: str):
    print(module_path)


@RequestMapping('/framework/ip/count', ['get', 'post'])
@ResponseBody()
def view_ip_count():
    """
    此为公共请求,不计入ip统计
    :return:
    """
    return ip_count


@RequestMapping('/framework/ip/refuse', ['get', 'post'])
@ResponseBody()
def view_ip_refuse():
    """
    此为公共请求,不计入ip统计
    :return:
    """
    return ip_refuse_list


GC_INFO = properties.debug_trace if properties.debug_trace else False  # gc信息开关


@RequestMapping('/framework/gc/show', ['get'])
@ResponseBody()
def show_gc_info():
    # return gc.show_gc_leak(print)
    return gc.show_gc_leak(logger.info) if GC_INFO else {}


@GetRoute('/rule/<view>')
def show_rule_info(view):
    __bind_rule_info_map = {}

    for item in get_app().url_map.iter_rules():
        # print(next(get_app().url_map.iter_rules(item.endpoint)))
        # print(re.sub('_annotation_auto_reg\.', '', item.endpoint))

        __bind_rule_info_map[str(next(get_app().url_map.iter_rules(item.endpoint)))] = \
            re.sub('_annotation_auto_reg\.', '', item.endpoint)

    # print([ v for v in sorted(__bind_rule_info_map.values())] )

    from .annotation.description import DESC_INFO

    # print(DESC_INFO)

    try:
        def __sort_inner_desc_info(item_key: str):
            def parse_param(info: dict):
                __result = ''
                for __param_name, __param_info in info.items():
                    __result += f'''<div style="margin: 10px;"><span class="label label-primary">
                                    {__param_name}
                                </span></div>'''
                    __result += '<table class="table table-hover table-striped"><tbody>'
                    for __name, __value in __param_info.items():
                        __result += f'''<tr><td class="">{__name}</td><td class="">{escape(str(__value))}</td></tr>'''
                    __result += '</tbody></table>'
                return __result

            result = ''
            if __bind_rule_info_map[item_key] in DESC_INFO:
                __desc_info = DESC_INFO[__bind_rule_info_map[item_key]]
            else:
                return result
            for __arg_name, __arg_info in __desc_info.items():
                result += f"""
                    <div class="panel panel-default">
                            <div class="panel-heading">
                                <h4 class="panel-title">
                                        {'Doc' if __arg_name == 'own_doc' else 'Params'}
                                </h4>
                            </div>
                            <div id="collapse_{id(__arg_name)}_{id(__arg_info)}" class="panel-collapse">
                                <div class="panel-body">
                                    { __arg_info if __arg_name == 'own_doc' else parse_param(__arg_info) }
                                </div>
                            </div>
                        </div>
                    """
            return result

        # 注册路径列表入口

        #    {'</div></div><div class="ivu-card ivu-card-bordered"><div class="ivu-card-body">'.join(
        #     [
        #         str(item)
        #         for item in get_app().url_map.iter_rules()
        #
        #     ]
        # )}
        body_str = ''
        for item in get_app().url_map.iter_rules():
            route_method_path = __bind_rule_info_map[str(item)]
            if re.search('\.', route_method_path) and not re.match('FrameworkStaticRoute\..*', route_method_path):
                # 非框架定义的路由参与路由显示
                body_str += f"""<div class="panel panel-default">
                        <div class="panel-heading">
                            <h4 class="panel-title">
                                <a data-toggle="collapse" 
                                   href="#collapse_{id(item)}">
                                    {escape(str(item))}
                                    <span class="label label-primary" style="float:right;">
                                        {route_method_path}
                                    </span
                                </a>
                            </h4>
                        </div>
                        <div id="collapse_{id(item)}" class="panel-collapse collapse">
                            <div class="panel-body">
                                { __sort_inner_desc_info(str(item)) }
                            </div>
                        </div>
                    </div>"""

        return f"""
                <html>
                <head>
                    <meta charset="utf-8"> 
                    <title>infos</title>
                    <link rel="stylesheet" href="https://cdn.staticfile.org/twitter-bootstrap/3.3.7/css/bootstrap.min.css">
                    <script src="https://cdn.staticfile.org/jquery/2.1.1/jquery.min.js"></script>
                    <script src="https://cdn.staticfile.org/twitter-bootstrap/3.3.7/js/bootstrap.min.js"></script>
                    <style>
                        """"""
                        td {
                            width:50%;
                            text-align:left;
                        }
                        """f"""
                    </style>
                </head>
                <body>
                       <div class="panel-group" id="accordion">
                       {body_str}
                       </div>
                
                </body>
                </html>
           """ if view == 'map' else jsonify([
            str(item)
            for item in get_app().url_map.iter_rules()

        ]) if view == 'json' else abort(404)
    except AssertionError:
        pass


# endregion

# region 定义报错页面

from dophon.tools.framework_const import error_info_type, self_result


@app.errorhandler(500)
def handle_500(e):
    """
    处理业务代码异常页面
    :param e:
    :return:
    """
    exc_type, exc_value, exc_tb = sys.exc_info()
    tc = traceback.format_tb(exc_tb)
    if properties.debug_trace:
        trace_detail = '<h4>Details</h4>'
        trace_detail += '<table style="width:100%;" cellspacing="0" cellpadding="4">'
        for tc_item in tc:
            if tc_item.find(os.getcwd()) < 0:
                continue
            trace_detail += '<tr>'
            tc_item_info_list = tc_item.split(',', 2)
            # for tc_item_info_list_item in tc_item_info_list:
            #     trace_detail += '<td>' + tc_item_info_list_item + '</td>'
            trace_detail += '<td style="border: 1px solid gray;">' + re.sub('(^.+(\\\|/))|"', '',
                                                                            tc_item_info_list[0]) + '</td>'
            trace_detail += '<td style="border: 1px solid gray;">' + tc_item_info_list[1] + '</td>'
            trace_code_detail = re.sub('^\s+', '', tc_item_info_list[2]).split(' ', 1)
            trace_detail += '<td style="border: 1px solid gray;">' + ' => '.join([
                trace_code_detail[0],
                re.sub('\s+', ' => ', trace_code_detail[1], 1),
            ]) + '</td>'
            trace_detail += '<tr>'
        trace_detail += '</table>'
    else:
        trace_detail = ''
    if error_info == error_info_type.HTML:
        return '<h1>Wrong!!</h1>' + \
               '<h2>error info:' + str(e) + '</h2>' + \
               '<h3>please contact coder or direct to ' \
               '<a href="https://dophon.blog">dophon</a> and leave your question</h3>' + \
               trace_detail, 500
    elif error_info == error_info_type.JSON:
        return self_result.JsonResult(500, tc, """
        please contact coder or direct to dophon website and leave your question
        """).as_res()
    elif error_info == error_info_type.XML:
        return self_result.XmlResult(500, tc, """
        please contact coder or direct to dophon website and leave your question
        """).as_res()


@app.errorhandler(404)
def handle_404(e):
    """
    处理路径匹配异常
    :return:
    """
    global error_info
    if error_info == error_info_type.HTML:
        return '<h1>Wrong!!</h1>' + \
               '<h2>error info:' + str(e) + '</h2>' + \
               '<h3>please contact coder or direct to ' \
               '<a href="https://dophon.blog">dophon</a> and leave your question</h3>' + \
               'request path:' + request.path, 404
    elif error_info == error_info_type.JSON:
        return self_result.JsonResult(404, request.path, 'please check your path').as_res()
    elif error_info == error_info_type.XML:
        return self_result.XmlResult(404, request.path, 'please check your path').as_res()


@app.errorhandler(405)
def handle_405(e):
    """
    处理请求方法异常
    :return:
    """
    if error_info == error_info_type.HTML:
        return '<h1>Wrong!!</h1>' + \
               '<h2>error info:' + str(e) + '</h2>' + \
               '<h3>please contact coder or direct to ' \
               '<a href="https://dophon.blog">dophon</a> and leave your question</h3>' + \
               'request method:' + request.method, 405
    elif error_info == error_info_type.JSON:
        return self_result.JsonResult(405, {request.path, request.method}, 'please check your request method').as_res()
    elif error_info == error_info_type.XML:
        return self_result.XmlResult(405, {request.path, request.method}, 'please check your request method').as_res()


@app.errorhandler(400)
def handle_400(e):
    """
    处理异常请求
    :return:
    """
    if error_info == error_info_type.HTML:
        return ('<h1>Wrong!!</h1>' + \
                '<h2>error info:' + str(e) + '</h2>' + \
                '<h3>please contact coder or direct to '
                '<a href="https://dophon.blog">dophon</a> and leave your question</h3>' + \
                'request form:' + request.form + \
                'request body:' + request.json if request.is_json else ''), 400
    elif error_info == error_info_type.JSON:
        return self_result.JsonResult(400, request.json if request.is_json else '',
                                      'please check your request data').as_res()
    elif error_info == error_info_type.XML:
        return self_result.XmlResult(400, request.json if request.is_json else '',
                                     'please check your request data').as_res()

# endregion
