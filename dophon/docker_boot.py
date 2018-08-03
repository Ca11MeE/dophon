from dophon import boot

import re

import os

import sys

from dophon import logger, properties

logger.inject_logger(globals())


def run_as_docker():
    """
    利用docker启动项目
    :return:
    """
    try:
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
            file.write('ADD . ' + work_dir + '/' + work_dir + '\n')
            file.write('WORKDIR ' + work_dir + '\n')
            file.write('RUN pip install -r requirements.txt' + '\n')
            file.write('CMD ["python","./Bootstrap.py"]' + '\n')
            # file.write('CMD ["/bin/bash"]' + '\n')
        os.system('cd ' + root)
        logger.info('暂停已运行的实例')
        os.system('docker stop ' + os.path.basename(root))
        logger.info('移除已运行的实例')
        os.system('docker rm ' + os.path.basename(root))
        logger.info('移除旧镜像')
        os.system('docker rmi ' + os.path.basename(root))
        logger.info('建立镜像')
        os.system('docker build -t ' + os.path.basename(root) + ' .')
        logger.info('运行镜像')
        os.system(
            'docker run -p ' + port_str + ':' + port_str + ' -d --name ' + os.path.basename(root) + ' ' + os.path.basename(
                root))
        logger.info('进入镜像')
        os.system(
            'docker attach ' + os.path.basename(root))
    except Exception as e:
        print(e)
