# coding: utf-8
import os
import time
import random
import datetime
import json
from threading import Thread
from dophon import logger

logger.inject_logger(globals())

def full_0(string: str, num_of_zero: int) -> str:
    if len(string) < num_of_zero:
        string = string.rjust(num_of_zero, '0')
    return string


def threadable():
    def method(f):
        def args(*args, **kwargs):
            Thread(target=f, args=args, kwargs=kwargs).start()

        return args

    return method


def producer(tag: str, delay: int = 0):
    def method(f):
        def args(*args, **kwargs) -> dict:
            time.sleep(delay)
            # 执行被装饰方法,检查返回值
            result = f(*args, **kwargs)
            try:
                # 发送消息
                msg_mark = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + full_0(
                    str(random.randint(0, 999999999999)), 6)
                if not os.path.exists('./' + tag):
                    os.mkdir(tag)
                with open('./' + tag + '/' + msg_mark, 'w') as file:
                    json.dump(result, file, ensure_ascii=False)
            except:
                raise Exception('无法识别的消息类型')

        return args

    return method


def consumer(tag: str, delay: int = 1, retry: int = 3, as_args: bool = False):
    def method(f):
        @threadable()
        # 启用多线程监听消息
        def args(*args, **kwargs):
            while True:
                for root, dirs, files in os.walk('./' + tag):
                    for name in files:
                        retrys = 0
                        while retrys < retry:
                            try:
                                file_path = os.path.join(root, name)
                                with open(file_path, 'r') as file:
                                    new_kwargs = json.load(file)
                                    if as_args:
                                        f(args=new_kwargs)
                                    else:
                                        f(**new_kwargs)
                            except TypeError as te:
                                print(te)
                            else:
                                os.remove(file_path)
                                break
                            finally:
                                retrys += 1
                                time.sleep(delay)
                                if retrys >= retry:
                                    logger.error('超出重试次数,文件名 %s', (file_path,))
                                    # 超出重试后重命名文件
                                    msg_mark = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + full_0(
                                        str(random.randint(0, 999999999999)), 6)
                                    logger.debug('新文件名 %s', (str(msg_mark),))
                                    n_file_path=os.path.join(root, msg_mark)
                                    os.rename(file_path, n_file_path)

        return args

    return method


@producer(tag='test_msg_tag')
def produce_msg(mark):
    return {'msg': '一条消息' + str(mark), 'timestamp': datetime.datetime.now().timestamp()}


@consumer(tag='test_msg_tag', as_args=False, delay=1)
def consume_msg(msg, timestamp):
    print(msg)
    print(timestamp)


produce_msg(1)
produce_msg(2)
produce_msg(3)
produce_msg(4)
consume_msg()
produce_msg(5)
produce_msg(6)
produce_msg(7)
produce_msg(8)
