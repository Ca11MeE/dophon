from dophon.msg_queue import *

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


@producer(tag=['DEMO_TAGa', 'DEMO_TAGb', 'DEMO_TAGc'])
def produce1():
    return 'aaa'


@producer(tag=['DEMO_TAGd', 'DEMO_TAGe', 'DEMO_TAGf'], delay=1)
def produce2():
    return 'bbb'


@producer(tag=['DEMO_TAGg', 'DEMO_TAGh', 'DEMO_TAGi'])
def produce3():
    return 'ccc'


@producer(tag=['DEMO_TAGi'])
def produce4():
    return 'ddd'


@consumer(tag=['DEMO_TAGa', 'DEMO_TAGb', 'DEMO_TAGc'], as_args=True)
def consume1(args):
    print(args)


@consumer(tag=['DEMO_TAGd', 'DEMO_TAGe', 'DEMO_TAGf'], as_args=True)
def consume2(args):
    print(args)


@consumer(tag=['DEMO_TAGg', 'DEMO_TAGh', 'DEMO_TAGi'], as_args=True, delay=2)
def consume3(args):
    print(args)


if '__main__' == __name__:
    # produce1()
    # produce2()
    # produce3()
    produce4()
    consume1()
    consume2()
    consume3()
