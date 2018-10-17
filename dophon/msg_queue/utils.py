"""
常用工具
"""
import os
from threading import Thread
import functools


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
