from dophon.msg_queue.MsgCenter import SocketMsgTunnel
import os
from dophon.msg_queue import *


@producer(tag='test_tag')
def send_remote():
    return 'sss'


@consumer(tag='test_tag')
def get_remote(args):
    print(args)
    return args


print(send_remote())
print(get_remote(''))
