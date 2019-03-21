import os
from subprocess import Popen, PIPE, DEVNULL

from dophon_properties import *
from tqdm import tqdm

get_property(DOPHON)
from dophon_logger import *

get_logger(DOPHON).inject_logger(globals())

from dophon.tools import is_windows
from importlib import util


def __dynamic_import(module_name, version='*'):
    __module = None
    while True:
        try:
            # 校验模块安装
            util.find_spec(f'{module_name}')
            # exec(f'import {module_name}')
            module = __module if __module else __import__(module_name)
            # sys.modules[module_name] = module
            logger.info(f'模块{module_name}依赖建立完毕')
            return module
        except Exception as e:
            # print(e)
            logger.info(f"install {module_name} >={version if version else 'release'}")
            # 利用pip模块安装所需模块
            pip_arg_list = ['pip', 'install',
                            module_name + (('>=' + version) if version else ''),
                            '--user']
            exe_pip_args = ['install',
                            module_name + (('>=' + version) if version else ''),
                            '--user']
            if not version:
                pip_arg_list.append('-U')
                exe_pip_args.append('-U')
            # 利用popen执行命令安装包
            # p = Popen(f'pip install {module_name} {"" if is_windows() else "--user"}', stdout=DEVNULL, stderr=DEVNULL)
            p = Popen(f'pip install {module_name} {"" if is_windows() else "--user"}',stdout=PIPE,stderr=PIPE)
            p.wait()
            # tqdm(p.stdout.readlines(), f'install {module_name}')
            lines_queue = tqdm(p.stdout.readlines())
            for item in lines_queue:
                lines_queue.set_description(item)
            __module = __import__(module_name)


def __d_import(module_name: str, version: str = '*'):
    """
    将需要安装的包信息放入全局字典中
    :param module_name:
    :param version:
    :return:
    """
    while True:
        try:
            __import__(module_name)
            break
        except Exception as e:
            # print(e)
            __dynamic_import(module_name=module_name, version=version)


def d_import(module_name, version: str = '*'):
    """
    对外暴露的动态添加函数入口
    :param module_name:
    :param version:
    :return:
    """
    __d_import(module_name=module_name, version=version)
    restart_program()


# 重启程序
def restart_program():
    python = sys.executable
    os.execl(python, python, *sys.argv)
