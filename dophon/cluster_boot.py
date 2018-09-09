# -*- coding: utf-8 -*-
from multiprocessing import Process, freeze_support
import time, socket, random
from flask import request, make_response
from urllib3 import PoolManager

ports = []  # 记录监听端口

proxy_clusters = {}

pool = PoolManager()


def main_freeze():
    freeze_support()


def redirect_request():
    print(request.path)
    res = pool.request(request.method, '127.0.0.1:' + str(random.choice(ports)) + request.path,
                       fields=request.json if request.is_json else request.form)
    return make_response(res.data)


def outer_entity(boot):
    # 重写路由信息(修改为重定向路径)
    boot.get_app().before_request(redirect_request)
    boot.run_app()


def run_clusters(clusters: int, **kwargs):
    from dophon import boot
    for i in range(clusters):
        current_port = kwargs['port'] + i
        create_cluster_cell(boot=boot, port=current_port)
        ports.append(current_port)
    while len(ports) != clusters:
        time.sleep(5)

    print('启动检测端口监听')
    for port in ports:
        if check_socket(int(port)):
            continue
    print('集群端口: %s ' % ports)

    print('启动外部端口监听')
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
