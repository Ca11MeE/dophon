"""
消息处理中心

处理消息发送信息落地
初始化消息通道（单一消息通道模式，集群消息通道模式）
"""
import datetime
import random
import json
import time
from dophon.msg_queue.utils import *
from threading import Timer
from dophon import logger
import re

logger.inject_logger(globals())


@singleton
def get_center(debug: bool = False):
    return MsgCenter(debug)


class MsgCenter():
    _p_name_l = []
    _p_tunnel_cursor = {}

    def __init__(self, debug: bool):
        logger.info('初始化消息中心')
        if debug:
            self.listen_p_book()

    def write_p_book(self, p_name):
        """
        登记生产属性名单
        :param p_name: 生产名
        :param p_id: 生产标识（用作生产校验）
        :return:
        """
        if p_name not in self._p_name_l \
                and p_name not in self._p_tunnel_cursor \
                and not self._p_tunnel_cursor.get(p_name):
            self._p_name_l.append(p_name)
            m_tunnel = MsgTunnel(p_name)
            self._p_tunnel_cursor[p_name] = m_tunnel

    @threadable()
    def listen_p_book(self):
        self.print_trace_manager()

    def print_trace_manager(self):
        while True:
            time.sleep(3)
            print(trace_manager)

    def do_send(self, msg, p_name, delay):
        """
        发送消息
        :param msg:
        :param p_name:
        :param delay:
        :return:
        """
        # 使用定时器发送消息
        timer = Timer(delay, self._p_tunnel_cursor[p_name].recv_msg, [msg])
        timer.start()
        self._p_tunnel_cursor[p_name].insert_msg(p_name)

    # 启用多线程监听消息
    @threadable()
    def do_get(self, p_name, delay: int):
        if p_name and p_name in self._p_tunnel_cursor:
            print('监听：', p_name)
            self._p_tunnel_cursor[p_name].query_msg(delay)


class MsgTunnel():
    """
    消息隧道
    """
    __queue = {}
    __k_queue = []

    def __init__(self, p_name):
        self._p_name = p_name

    def __str__(self):
        return str(id(self))

    def recv_msg(self, msg):
        try:
            # 发送消息
            msg_mark = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + full_0(
                str(random.randint(0, 999999999999)), 6)
            if not os.path.exists(msg_pool + self._p_name):
                os.mkdir(msg_pool + self._p_name)
            with open(msg_pool + self._p_name + '/' + msg_mark, 'w') as file:
                json.dump(msg, file, ensure_ascii=False)
        except:
            raise Exception('无法识别的消息类型')

    def insert_msg(self, tag):
        """
        装载消息
        :param tag:
        :return:
        """
        self.__k_queue.clear()
        for root, dirs, files in os.walk(msg_pool + tag):
            for name in files:
                file_path = os.path.join(root, name)
                with open(file_path, 'r') as file:
                    new_kwargs = json.load(file)
                    # 加载消息
                    self.__queue[name] = {
                        'msg': new_kwargs,
                        'file_path': file_path
                    }
        self.__k_queue = list(self.__queue.keys())

    def query_msg(
            self,
            delay: int
    ):
        """
        查询隧道信息
        :return:
        """
        while True:
            time.sleep(delay)
            if self.__k_queue:
                # 获取信息
                msg_k = self.__k_queue.pop(0)
                msg_obj = self.__queue.pop(msg_k)
                __r_file_path = re.sub('\\\\', '/', msg_obj['file_path'])
                print(msg_obj['msg'])
                try:
                    # 消息消费成功
                    # 清除消息
                    os.remove(__r_file_path)
                except Exception as e:
                    print(e)
            # for root, dirs, files in os.walk(msg_pool + tag):
            #     if files:
            #         for name in files:
            #             retrys = 0
            #             file_path = os.path.join(root, name)
            #             while retrys < retry:
            #                 try:
            #                     with open(file_path, 'r') as file:
            #                         new_kwargs = json.load(file)
            #                         # 执行失败启动重试流程
            #                         if as_args:
            #                             f(args=new_kwargs)
            #                         else:
            #                             f(**new_kwargs)
            #                 except TypeError as te:
            #                     logger.error('%s: %s', name, te)
            #                     trace_manager[tag] = {
            #                         'type': 'TypeError',
            #                         'msg': traceback.format_exc()
            #                     }
            #                 except FileNotFoundError as fnfe:
            #                     logger.error('%s: %s', name, fnfe)
            #                     trace_manager[tag] = {
            #                         'type': 'FileNotFoundError',
            #                         'msg': traceback.format_exc()
            #                     }
            #                 except Exception as e:
            #                     logger.warning('%s: %s', name, e)
            #                     trace_manager[tag] = {
            #                         'type': 'Exception',
            #                         'msg': traceback.format_exc()
            #                     }
            #                 else:
            #                     os.remove(file_path)
            #                     break
            #                 finally:
            #                     retrys += 1
            #                     time.sleep(delay)
            #                     if retrys >= retry:
            #                         logger.error('超出重试次数,文件名 %s', file_path)
            #                         # 超出重试后重命名文件
            #                         msg_mark = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + full_0(
            #                             str(random.randint(0, 999999999999)), 6)
            #                         logger.debug('新文件名 %s', str(msg_mark))
            #                         n_file_path = os.path.join(root, msg_mark)
            #                         try:
            #                             os.rename(file_path, n_file_path)
            #                         except FileNotFoundError as fnfe:
            #                             # 消息已被消费或已被重命名
            #                             logger.warning('消息已被消费: %s', file_path, '::::', fnfe)
            self.insert_msg(self._p_name)
