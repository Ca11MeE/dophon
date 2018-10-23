from dophon.msg_queue.MsgCenter import SocketMsgTunnel

if __name__ == '__main__':
    SocketMsgTunnel('DEMO_TAGi').send_msg('哈哈哈')
    SocketMsgTunnel('DEMO_TAGa').send_msg('哈哈哈')
    SocketMsgTunnel('DEMO_TAGb').send_msg('哈哈哈')
    while True:
        pass
