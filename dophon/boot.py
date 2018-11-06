# coding: utf-8
import traceback, functools
import os,sys,re
from threading import *
import json
"""
初始化协程模块(必须,不然导致系统死锁)
"""
from gevent import monkey

monkey.patch_all()

from dophon import pre_boot, logger

logger.inject_logger(globals())

pre_boot.check_modules()

from flask import Flask, request, abort
from dophon import properties

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


# 处理各模块中的自动注入以及组装各路由
# dir_path中为路由模块路径,例如需要引入的路由都在routes文件夹中,则传入参数'/routes'
def map_apps(dir_path):
    path = os.getcwd() + dir_path
    if not os.path.exists(path):
        logger.error('路由文件夹不存在,创建路由文件夹')
        os.mkdir(path)
    f_list = os.listdir(path)
    logger.info('路由文件夹: %s', dir_path)
    while f_list:
        try:
            file = f_list.pop(0)
            if re.match('__.*__', file):
                continue
            i = os.path.join(path, file)
            if os.path.isdir(i):
                logger.info('加载路由模块: %s', file)
                continue
            f_model = __import__(re.sub('/', '', dir_path) + '.' + re.sub('\.py', '', file), fromlist=True)
            filter_method = f_model.app.before_request(before_request)
            if hasattr(properties, 'ip_count') and getattr(properties, 'ip_count'):
                setattr(f_model, 'before_request', filter_method)
            app.register_blueprint(f_model.app)
        except Exception as e:
            raise e
            pass


logger.info('路由初始化')
for path in properties.blueprint_path:
    map_apps(path)


def get_app() -> Flask:
    return app


def free_source():
    def method(f):
        @functools.wraps(f)
        def args(*arg, **kwarg):
            logger.info('启动服务器')
            load_footer()
            f(*arg, **kwarg)
            """
            释放所有资源
            :return:
            """
            logger.info('服务器关闭')
            logger.info('释放资源')
            if mysql:
                mysql.free_pool()
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
    logger.info('监听地址: %s : %s' % (host, port))
    if properties.server_gevented:
        from gevent.pywsgi import WSGIServer
        WSGIServer((host, port), app).serve_forever()
    else:
        # 开启多线程处理
        app.run(host=host, port=port, threaded=properties.server_threaded)


@free_source()
def run_app_ssl(host=properties.host, port=properties.port, ssl_context=properties.ssl_context):
    logger.info('监听地址: %s : %s' % (host, port))
    if properties.server_gevented:
        from gevent.pywsgi import WSGIServer
        ssl_args = {
            'certfile': ssl_context[0],
            'keyfile': ssl_context[1],
        }
        WSGIServer((host, port), app, **ssl_args).serve_forever()
    else:
        # 开启多线程处理
        app.run(host=host, port=port, ssl_context=ssl_context, threaded=properties.server_threaded)


def bootstrap_app():
    """
    bootstrap样式页面初始化
    :return:
    """
    global app
    b = __import__('flask_bootstrap')
    b.Bootstrap(app)


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
    return '<h1>Wrong!!</h1>' + \
           '<h2>error info:' + str(e) + '</h2>' + \
           '<h3>please contact coder or direct to <a href="https://dophon.blog">dophon</a> and leave your question</h3>' + \
           trace_detail, 500


@app.errorhandler(404)
def handle_404(e):
    """
    处理路径匹配异常
    :return:
    """
    return '<h1>Wrong!!</h1>' + \
           '<h2>error info:' + str(e) + '</h2>' + \
           '<h3>please contact coder or direct to <a href="https://dophon.blog">dophon</a> and leave your question</h3>' + \
           'request path:' + request.path, 404


@app.errorhandler(405)
def handle_405(e):
    """
    处理请求方法异常
    :return:
    """
    return '<h1>Wrong!!</h1>' + \
           '<h2>error info:' + str(e) + '</h2>' + \
           '<h3>please contact coder or direct to <a href="https://dophon.blog">dophon</a> and leave your question</h3>' + \
           'request method:' + request.method, 405


@app.errorhandler(400)
def handle_400(e):
    """
    处理异常请求
    :return:
    """
    return ('<h1>Wrong!!</h1>' + \
           '<h2>error info:' + str(e) + '</h2>' + \
           '<h3>please contact coder or direct to <a href="https://dophon.blog">dophon</a> and leave your question</h3>' + \
           'request form:' + request.form + \
           'request body:' + request.json if request.is_json else ''), 400
