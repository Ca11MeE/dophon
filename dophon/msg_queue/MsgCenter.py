"""
消息处理中心

处理消息发送信息落地
初始化消息通道（单一消息通道模式，集群消息通道模式）
"""
import datetime
import random
import json
import time
from socketserver import *

from dophon.msg_queue.utils import *
from threading import Timer
from dophon import logger
import re
from socket import socket
from dophon import properties

logger.inject_logger(globals())


@singleton
def get_center(debug: bool = False, remote_center: bool = False):
    ins_obj = MsgCenter(debug, remote_center)
    if remote_center:
        logger.info('开启远程消息')
    return ins_obj


class MsgCenter():
    _p_name_l = []
    _p_tunnel_cursor = {}

    def __init__(self, debug: bool, remote_center: bool = False):
        logger.info('初始化消息中心')
        if debug:
            self.listen_p_book()
        # 记录远程中心标识
        self._remote_flag = remote_center

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
            if self._remote_flag:
                m_tunnel = SocketMsgTunnel(p_name)
                self._p_tunnel_cursor[p_name] = m_tunnel
            else:
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
        :param msg: 消息体
        :param p_name: 消息标签
        :param delay: 延时
        :return:
        """
        if self._remote_flag:
            self.do_remote_send(msg, p_name, delay)
        else:
            self.do_local_send(msg, p_name, delay)

    def do_local_send(self, msg, p_name, delay):
        # 使用定时器发送消息
        timer = Timer(delay, self._p_tunnel_cursor[p_name].recv_msg, [msg])
        timer.start()
        self._p_tunnel_cursor[p_name].insert_msg(p_name)

    def do_remote_send(self, msg, p_name, delay):
        """
        发送消息到消息通道
        :param msg:
        :param p_name: 消息标签
        :param delay: 延时
        :return: 消息体
        """
        # 使用定时器发送消息
        timer = Timer(delay, self._p_tunnel_cursor[p_name].send_msg, [msg])
        timer.start()
        self._p_tunnel_cursor[p_name].insert_msg(p_name)

    # 启用多线程监听消息
    @threadable()
    def do_get(self, p_name, delay: int):
        """
        从消息管道获取消息
        :param p_name:
        :param delay:
        :return:
        """
        if p_name and p_name in self._p_tunnel_cursor:
            self._p_tunnel_cursor[p_name].query_msg(delay)


class MsgTunnel:
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
        except Exception as e:
            raise Exception('无法识别的消息类型,原因: %s', e)

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
            self.insert_msg(self._p_name)


class SocketMsgTunnel(MsgTunnel):
    def __init__(self, p_name: str):
        super(SocketMsgTunnel, self).__init__(p_name)
        # 实例内部套接字初始化
        self.__socket = socket()
        self.__socket.connect((properties.mq.get('remote_address'), properties.mq.get('remote_port')))
        self._p_name = p_name

    def send_msg(self, msg):
        bound_dict = {
            'tag': self._p_name,
            'msg': msg
        }
        try:
            # 尝试发送消息
            self.__socket.sendall(bytes(json.dumps(bound_dict), encoding="utf-8"))
            print('发送成功')
            print(str(self.__socket.recv(1024),encoding='utf-8'))
        except Exception as e:
            print('发送失败', msg,'原因',e)
