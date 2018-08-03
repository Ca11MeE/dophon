# coding: utf-8
import os
import time
import random
import datetime
import json
from threading import Thread
from dophon import logger,properties
import inspect
import re
import traceback
from concurrent.futures import ThreadPoolExecutor

__all__ = [
    'producer', 'consumer'
]

logger.inject_logger(globals())

trace_manager = {}

max_workers=properties.msg_queue_max_num

pool = ThreadPoolExecutor(max_workers=max_workers)


def full_0(string: str, num_of_zero: int) -> str:
    if len(string) < num_of_zero:
        string = string.rjust(num_of_zero, '0')
    return string


def threadable():
    def method(f):
        def args(*args, **kwargs):
            # 采用线程池操作,减缓cpu压力
            pool.submit(f,*args, **kwargs)
        return args

    return method


def join_threadable():
    def method(f):
        def args(*args, **kwargs):
            Thread(target=f, args=args, kwargs=kwargs).join()
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
    tags = tag.split('|')

    def method(f):
        def queue_args(*args, **kwargs):
            @threadable()
            # 启用多线程监听消息
            def args(tag, *args, **kwargs):
                while True:
                    time.sleep(1)
                    for root, dirs, files in os.walk('./' + tag):
                        if files:
                            for name in files:
                                retrys = 0
                                while retrys < retry:
                                    try:
                                        file_path = os.path.join(root, name)
                                        with open(file_path, 'r') as file:
                                            new_kwargs = json.load(file)
                                            # 执行失败启动重试流程
                                            if as_args:
                                                f(args=new_kwargs)
                                            else:
                                                f(**new_kwargs)
                                    except TypeError as te:
                                        logger.error('%s: %s', name, te)
                                        trace_manager[tag] = {
                                            'type': 'TypeError',
                                            'msg': traceback.format_exc()
                                        }
                                    except Exception as e:
                                        logger.error('%s: %s', name, e)
                                        trace_manager[tag] = {
                                            'type': 'TypeError',
                                            'msg': traceback.format_exc()
                                        }
                                    else:
                                        os.remove(file_path)
                                        break
                                    finally:
                                        retrys += 1
                                        time.sleep(delay)
                                        if retrys >= retry:
                                            logger.error('超出重试次数,文件名 %s', file_path)
                                            # 超出重试后重命名文件
                                            msg_mark = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + full_0(
                                                str(random.randint(0, 999999999999)), 6)
                                            logger.debug('新文件名 %s', str(msg_mark))
                                            n_file_path = os.path.join(root, msg_mark)
                                            try:
                                                os.rename(file_path, n_file_path)
                                            except FileNotFoundError as fnfe:
                                                # 消息已被消费或已被重命名
                                                logger.warning('消息已被消费: %s', file_path)

            for tag in tags:
                args(tag)

        if len(tags) > 1:
            print('监听多个标签', tags)

        return queue_args

    return method


class Consumer:
    """
    消息消费者封装(带自动运行)
    """

    def __init__(self):
        """
        注意!!!!
        重写该类的init方法必须显式执行该类的init方法,否则定义的消息消费将失效
        """
        for name in dir(self):
            item = getattr(self, name)
            if not re.match('__.+__', name) and \
                    callable(item) and \
                    re.match('consumer.<locals>.method.<locals>.*', getattr(getattr(item, '__func__'), '__qualname__')):
                for nn in dir(inspect.getfullargspec(item)):
                    print(nn, '--', getattr(inspect.getfullargspec(item), nn))
                fields = inspect.getfullargspec(item).args
                # 清除自对象参数
                staticmethod(item(*fields))


"""

DEMO:

@producer(tag='test_msg_tag')
def produce_msg(mark):
    return {'msg': '一条消息' + str(mark), 'timestamp': datetime.datetime.now().timestamp(), 'tag': 'test_msg_tag'}


@producer(tag='test_msg_tag')
def produce_msg1(mark):
    return {'msg': '一条消息' + str(mark), 'timestamp': datetime.datetime.now().timestamp(), 'tag': 'test_msg_tag1'}


@producer(tag='test_msg_tag2')
def produce_msg2(mark):
    return {'msg': '一条消息' + str(mark), 'timestamp': datetime.datetime.now().timestamp(), 'tag': 'test_msg_tag2'}


class TestConsumer(Consumer):

    @consumer(tag='test_msg_tag|test_msg_tag2', as_args=False, delay=1)
    def consume_msg(msg, timestamp, tag):
        print(msg)
        print(timestamp)
        print(tag)

TestConsumer()

produce_msg(1)
produce_msg(2)
produce_msg1(3)
produce_msg1(4)
produce_msg2(5)
produce_msg2(6)
produce_msg1(7)
produce_msg2(8)
produce_msg(9)
produce_msg1(0)
"""

@producer(tag='DEMO_TAG')
def produce():
    return 'aaa'

@consumer(tag='DEMO_TAG')
def consume(args):
    print(args)

produce()
consume()