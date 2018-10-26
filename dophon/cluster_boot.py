# -*- coding: utf-8 -*-
from gevent import monkey

monkey.patch_all()
from multiprocessing import Process, freeze_support
import time, socket, random
from flask import request, make_response
from urllib3 import PoolManager
from dophon import logger
from dophon import properties

logger.inject_logger(globals())

ports = []  # 记录监听端口

proxy_clusters = {}

pool = PoolManager()


def main_freeze():
    freeze_support()


def redirect_request():
    logger.info('touch path: %s [success]' % (request.path))
    res = pool.request(request.method, '127.0.0.1:' + str(random.choice(ports)) + request.path,
                       fields=request.json if request.is_json else request.form)
    return make_response(res.data)


def outer_entity(boot):
    # 重写路由信息(修改为重定向路径)
    boot.get_app().before_request(redirect_request)
    boot.run_app()


def run_clusters(clusters: int, outer_port: bool = False, start_port: int = 8800):
    """
    运行集群式服务器
    :param clusters: 集群个数
    :param outer_port: 是否开启外部端口映射(映射端口为用户配置文件中配置的端口)
    :param start_port: 集群起始监听端口
    :return:
    """
    from dophon import boot
    for i in range(clusters):
        current_port = start_port + i
        create_cluster_cell(boot=boot, port=current_port)
        ports.append(current_port)
    while len(ports) != clusters:
        time.sleep(5)

    logger.info('启动检测端口监听')
    for port in ports:
        if check_socket(int(port)):
            continue
    logger.info('集群端口: %s ' % ports)
    if outer_port:
        logger.info('启动外部端口监听[%s]' % (properties.port))
        outer_entity(boot)


def create_cluster_cell(boot, port):
    # http协议
    proc = Process(target=boot.run_app, kwargs={
        'host': '127.0.0.1',
        'port': port
    })
    proc.start()


def check_socket(port: int):
    s = socket.socket()
    flag = True
    while flag:
        try:
            ex_code = s.connect_ex(('127.0.0.1', port))
            flag = False
            return int(ex_code) == 0
        except Exception as e:
            time.sleep(3)
            continue
