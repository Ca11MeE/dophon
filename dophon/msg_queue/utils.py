"""
常用工具
"""
import os
from threading import Thread
import functools

from dophon import properties
from dophon.msg_queue.SizeableTPE import SizeableThreadPoolExecutor


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def full_0(string: str, num_of_zero: int) -> str:
    if len(string) < num_of_zero:
        string = string.rjust(num_of_zero, '0')
    return string


# 消息池(初步为本地缓存目录)
msg_pool = os.path.expanduser('~') + '/.dophon_msg_pool/'

if not os.path.exists(msg_pool):
    os.mkdir(msg_pool)


def join_threadable(f):
    def method(*args, **kwargs):
        Thread(target=f, args=args, kwargs=kwargs).start()

    return method


max_workers = properties.msg_queue_max_num

# pool = ThreadPoolExecutor(max_workers=max_workers)
pool = SizeableThreadPoolExecutor(max_workers=max_workers)

trace_manager = {}


def threadable():
    def method(f):
        def args(*args, **kwargs):
            pool.update_worker_size()
            # 采用线程池操作,减缓cpu压力
            pool.submit(f, *args, **kwargs)

        return args

    return method
