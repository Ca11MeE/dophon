import logging

import re

import os
import socket

import sys


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

from dophon import logger, properties

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
        s.shutdown(2)
        logger.info('%d is open' % port)
        raise Exception('端口被占用:' + port)
    except:
        logger.info('%d is down' % port)
        return False


def run_as_docker(
        entity_file_name: str = None,
        container_port: str = str(properties.port),
        docker_port: str = str(properties.port)
):
    """
    利用docker启动项目
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
            file.write('ADD . ' + work_dir + '/' + base_name + '\n')
            file.write('WORKDIR ' + work_dir + '\n')
            file.write('RUN pip install -r requirements.txt' + '\n')
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
        IsOpen('127.0.0.1', int(docker_port))
        logger.info('建立镜像')
        build_id = os.system('docker build -t ' + base_name + ' .')
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
        logger.info('打印容器内部地址')
        os.system('docker inspect --format=\'{{.NetworkSettings.IPAddress}}\' ' + base_name)
        logger.info('进入镜像')
        os.system(
            'docker attach ' + base_name)

    except Exception as e:
        logger.error(build_id)
        print(e)
