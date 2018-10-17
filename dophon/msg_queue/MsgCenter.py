"""
消息处理中心

处理消息发送信息落地
初始化消息通道（单一消息通道模式，集群消息通道模式）
"""
import datetime
import random
import json
from dophon.msg_queue.utils import *
from threading import Timer


class MsgCenter():
    _p_name_l = []
    _p_tunnel_cursor = {}

    def __init__(self):
        print('初始化消息中心')

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
            print('登记生产信息！！！', p_name)
            self._p_name_l.append(p_name)
            print('生成生产隧道!!!')
            m_tunnel = MsgTunnel(p_name)
            self._p_tunnel_cursor[p_name] = m_tunnel
        # 打印隧道信息
        print(self._p_tunnel_cursor)
        for t_n, t in self._p_tunnel_cursor.items():
            print(t_n)
            print(t)

    def listen_p_book(self):
        pass

    def do_send(self, msg, p_name, delay):
        """
        发送消息
        :param msg:
        :param p_name:
        :param delay:
        :return:
        """
        timer = Timer(delay, self._p_tunnel_cursor[p_name].recv_msg, (msg,))
        timer.start()



class MsgTunnel():
    """
    消息隧道
    """

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
