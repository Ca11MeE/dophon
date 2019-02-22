from multiprocessing import Process
from multiprocessing.pool import ThreadPool
from subprocess import Popen, PIPE

from dophon_properties import *
from tqdm import tqdm

get_property(DOPHON)
from dophon_logger import *

get_logger(DOPHON).inject_logger(globals())

from dophon.tools import is_windows


def __dynamic_import(module_name, version='*'):
    __module = None
    while True:
        try:
            # 校验模块安装
            # exec(f'import {module_name}')
            module = __module if __module else __import__(module_name)
            sys.modules[module_name] = module
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
            p = Popen(f'pip install {module_name} {"" if is_windows() else "--user"}', stdout=PIPE, stderr=PIPE)
            for item in tqdm(p.stdout.readlines()):
                pass
            p.wait()
            __module = __import__(module_name)


def __d_import(*args, **kwargs):
    __dynamic_import(*args, **kwargs)


global_list = {}
global_pool = ThreadPool()


def __push_in_import_queue(module_name: str, version: str = '*'):
    """
    将需要安装的包信息放入全局字典中
    :param module_name:
    :param version:
    :return:
    """
    global global_list
    while True:
        try:
            __import__(module_name)
            break
        except:
            if module_name not in global_list:
                global_list[module_name] = version


def __start_listen_global_list():
    logger.info('启动监听')
    __executed_list = set()
    while True:
        # print(__executed_list)
        # print(global_list)
        # 全部已执行则跳出死循环
        if __executed_list and global_list and len(__executed_list) == len(global_list):
            break
        # 不停执行监听
        for k, v in global_list.items():
            # 判断标准:
            # 包标识已经在本次启动安装
            # 包标识已存在系统域中
            if k in sys.modules:
                __executed_list.add(k)
                continue
            if k in __executed_list:
                continue
            else:
                logger.info(f'执行引入包{k},{v}')
                # 执行引入包
                __d_import(module_name=k, version=v)
                # 添加到已安装集
                __executed_list.add(k)
    logger.info('监听完毕')


def d_import(module_name, version: str = '*'):
    """
    对外暴露的动态添加函数入口
    :param module_name:
    :param version:
    :return:
    """
    __push_in_import_queue(module_name, version)


def __apply_to_pool():
    global_pool.apply_async(func=__start_listen_global_list)


main_thread = Process(target=__apply_to_pool)
main_thread.run()
