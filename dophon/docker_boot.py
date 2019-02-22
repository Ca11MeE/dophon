# encoding: utf-8
from dophon.tools import is_windows
from . import boot
import logging

import re

import os
import socket

import sys
import threading

import time
from urllib import request


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

from dophon import properties
from dophon_logger import *

logger = get_logger(DOPHON)

logger.inject_logger(globals())


def IsOpen(ip, port):
    """
    检查端口是否被占用
    :param ip:
    :param port:
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        logger.error('端口被占用:' + port)
        s.close()
        return True
    except:
        return False


def listen(code):
    """
    监听命令状态码
    :param code: os.system()命令返回码
    :return: 当不正常执行会抛出错误,谨慎使用!!!
    """
    if code >> 8 is 0:
        pass
    else:
        raise Exception('命令执行错误!')


def listen_container_status(container_port, loop_count: int = 3, wait_sec: int = 10):
    """
    检测容器端口存活
    :return:
    """
    # 一分钟后检测
    time.sleep(60)
    # 默认检测三次
    curr_count = 1
    while int(curr_count) <= int(loop_count):
        # 默认间隔10秒
        time.sleep(wait_sec)
        if IsOpen(get_docker_address(), int(container_port)):
            raise Exception('端口映射异常')
        else:
            # 报错证明端口正常占用
            # 发起请求
            url = f'http://{get_docker_address()}:{container_port}/rule/json'
            logger.info('容器存活性检查:' + url)
            res = request.urlopen(url)
            if not res.read():
                raise Exception('服务启动异常')
        curr_count += 1
    logger.info('容器启动成功,请在命令行输入docker ps查看')


def get_docker_address():
    """
    获取容器载体ip
    :return:
    """
    result = os.popen('ipconfig' if is_windows() else 'ifconfig').readlines()
    result_lines = []
    r_l_copy = []
    while result:
        line = result[0]
        if re.search('^.*(d|D)(o|O)(c|C)(k|K)(e|E)(r|R).*$', line):
            result_lines = result.copy()
            break
        else:
            result.pop(0)
    for line in result_lines:
        line = re.sub('\s*', '', line)
        if line and re.search('([0-9]+\.)+[0-9]+$', line) and re.search('(i|I)(p|P)', line):
            r_l_copy.append(
                re.search('([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', line).group(0)
            )
    return r_l_copy.pop(0) if r_l_copy else 'can not get container ip'


def attach_container(base_name: str):
    """
    进入容器
    :return:
    """
    os.system('docker attach ' + base_name)


def run_as_docker(
        entity_file_name: str = None,
        container_port: str = str(properties.port),
        docker_port: str = str(properties.port),
        attach_cmd: bool = False,
        extra_package: dict = {},
        cache_virtual_env_dir: str = '',
        package_repository: str = '',
        package_cache_path: str = '',
):
    """
    利用docker启动项目
    :param entity_file_name: 入口文件名(包括后缀)
    :param container_port: 容器暴露端口
    :param docker_port: 容器内部端口 -> 集群模式下的暴露端口,一般为配置文件定义的端口
    :param attach_cmd: 是否进入容器内部sh
    :param extra_package: 额外需要加载的包以及版本
    :param cache_virtual_env_dir: 指定的虚拟器路径,在启动文件同级目录或下级目录
    :param package_repository: 自带缓存包路径,若为空会自动执行pip安装
                # 阿里云仓库  =>  https://mirrors.aliyun.com/pypi/simple/
    :param package_cache_path: 包缓存路径
    :return:
    """
    try:
        logger.info('容器前期准备')
        root = re.sub('\\\\', '/', properties.project_root)
        base_name = os.path.basename(root)
        import platform
        p_version = platform.python_version()
        work_dir = './' + base_name
        # 生成依赖文件
        logger.info('生成依赖文件')
        os.system('pip freeze --all >pre_requirements.txt')
        with open('./pre_requirements.txt', 'r') as file:
            with open('./requirements.txt', 'w') as final_file:

                for line in file.readlines():
                    for key in sys.modules.keys():
                        if re.search('(_|__|\\.).+$', key):
                            continue
                        module_path = re.sub('(>=|==|=>|<=|=<|<|>|=).*\s+', '', line.lower())
                        if re.search(module_path, key.lower()):
                            if module_path in extra_package:
                                final_file.write(f'{module_path}>={extra_package[module_path]}\n')
                                extra_package.pop(module_path)
                            else:
                                final_file.write(line)

                            continue
                # 写入额外包
                for package_name, package_version in extra_package.items():
                    if package_name in extra_package:
                        final_file.write(''.join([package_name, '>=', extra_package[package_name], '\n']))
                        # 会报迭代修改异常
                        # extra_package.popitem()
                    else:
                        final_file.write(''.join([package_name, '>=', package_version, '\n']))
        # 生成Dockerfile
        logger.info('生成Dockerfile')
        with open('./Dockerfile', 'w') as file:
            file.write('FROM python:' + p_version + '\n')
            file.write('ADD . ' + work_dir + '\n')
            file.write('ADD . ' + work_dir + '/' + base_name + '\n')
            file.write('WORKDIR ' + work_dir + '\n')
            if cache_virtual_env_dir:
                file.write(f'ADD {cache_virtual_env_dir} ~/.cache_virtual_env' + '\n')
                file.write(f'CMD ~/.cache_virtual_env/Scripts/activate' + '\n')
            if package_cache_path:
                file.write(f'ADD {package_cache_path} ~/.package_cache' + '\n')
                file.write(f'CMD python -m import sys;sys.path.append("~/.package_cache");' + '\n')
            if package_repository:
                # 阿里云仓库  =>  https://mirrors.aliyun.com/pypi/simple/
                file.write(f'RUN pip install -i {package_repository} -r requirements.txt' + '\n')
            else:
                file.write('RUN pip install --no-cache-dir -r requirements.txt' + '\n')
            file.write('CMD ["python","./' + (entity_file_name if entity_file_name else 'Bootstrap.py') + '"]' + '\n')
            # file.write('CMD ["/bin/bash"]' + '\n')
        os.system('cd ' + root)
        logger.info('暂停已运行的实例')
        os.system('docker stop ' + base_name)
        logger.info('移除已运行的实例')
        os.system('docker rm ' + base_name)
        logger.info('移除旧镜像')
        os.system('docker rmi ' + base_name)
        logger.info('检测配置合法性')
        if IsOpen('127.0.0.1', int(docker_port)):
            # 端口被占用
            logger.warn('映射端口被占用!!')
        logger.info('建立镜像')
        listen(os.system('docker build -t ' + base_name + ' .'))
        logger.info('运行镜像')
        os.system(
            'docker run -p ' + container_port
            +
            ':' +
            docker_port +
            ' -d --name ' +
            base_name + ' ' +
            os.path.basename(
                root))
        logger.info('打印容器内部地址(空地址代表启动失败)')
        os.system('docker inspect --format=\'{{.NetworkSettings.IPAddress}}\' ' + base_name)
        logger.info('打印容器载体地址')
        print(get_docker_address())
        logger.info('启动检测容器端口')
        threading.Thread(target=listen_container_status, args=(container_port,)).start()
        if attach_cmd:
            logger.info('进入镜像')
            # threading.Thread(target=attach_container,args=(base_name,)).start()
            attach_container(base_name)
        logger.info('容器启动完毕')
    except Exception as e:
        logger.error(e)
