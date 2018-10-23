import json
from datetime import time
from socketserver import ThreadingTCPServer, BaseRequestHandler, StreamRequestHandler
from threading import Timer

from dophon import logger
from dophon.msg_queue.utils import threadable

logger.inject_logger(globals())

trace_manager = {}


class MsgCenter(ThreadingTCPServer):
    _p_name_l = []
    _p_tunnel_cursor = {}

    def __init__(self, debug: bool = False, port: int = 58800):
        logger.info('初始化远程消息中心')
        if debug:
            self.listen_p_book()
        super(MsgCenter, self).__init__(('0.0.0.0', port), SocketMsgHandler)
        self.start_server()

    def start_server(self):
        self.serve_forever()

    @threadable()
    def listen_p_book(self):
        self.print_trace_manager()

    def print_trace_manager(self):
        while True:
            time.sleep(3)
            print(trace_manager)


class SocketMsgHandler(StreamRequestHandler):
    """
    远程消息隧道处理类
    """
    def handle(self):
        conn = self.request
        while True:
            ret_bytes = conn.recv(1024)
            ret_str = str(ret_bytes, encoding="utf-8")
            if ret_str:
                try:
                    data = json.loads(ret_str, encoding='utf-8')
                    if isinstance(data, dict):
                        # 处理消息
                        p_name = data['tag']
                        msg = data['msg']
                        print(p_name)
                        print(msg)
                        conn.sendall(bytes('接收消息: %s' % data, encoding='utf-8'))
                    else:
                        conn.sendall(bytes('不能识别的套接字', encoding='utf-8'))
                except Exception as e:
                    print(ret_str, '::', e)
