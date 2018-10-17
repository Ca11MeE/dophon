import os
from dophon import logger
from dophon import properties
import time
import random
import datetime
import json
import traceback
from dophon.msg_queue.SizeableTPE import SizeableThreadPoolExecutor

from dophon.msg_queue.utils import *

logger.inject_logger(globals())
trace_manager = {}

max_workers = properties.msg_queue_max_num

# pool = ThreadPoolExecutor(max_workers=max_workers)
pool = SizeableThreadPoolExecutor(max_workers=max_workers)


def threadable():
    def method(f):
        def args(*args, **kwargs):
            pool.update_worker_size()
            # 采用线程池操作,减缓cpu压力
            pool.submit(f, *args, **kwargs)

        return args

    return method


def consumer(tag: str, delay: int = 0, retry: int = 3, as_args: bool = False):
    tags = tag.split('|')

    def method(f):
        def queue_args(*args, **kwargs):
            # 启用多线程监听消息
            @threadable()
            def args(tag, *args, **kwargs):
                while True:
                    # time.sleep(1)
                    for root, dirs, files in os.walk(msg_pool + tag):
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
                                    except FileNotFoundError as fnfe:
                                        break
                                    except Exception as e:
                                        logger.warning('%s: %s', name, e)
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
                                                logger.warning('消息已被消费: %s', file_path, '::::', fnfe)

            for tag in tags:
                args(tag)

        if len(tags) > 1 and properties.msg_queue_debug:
            print('监听多个标签', tags)

        return queue_args

    return method
