from dophon import logger
from dophon.msg_queue import MsgCenter
from dophon.msg_queue.utils import *

center = MsgCenter.get_center()

logger.inject_logger(globals())


def consumer(tag: str, delay: int = 0, arg_name: str = 'args'):
    tags = tag if isinstance(tag, list) else tag.split('|')

    def method(f):
        def queue_args(*args, **kwargs):
            @threadable()
            def do_consume(tt):
                kwargs[arg_name] = center.do_get(tt, delay)
                return f(**kwargs)

            for t in tags:
                if arg_name in kwargs:
                    # 执行消息中心信息监听
                    do_consume(t)
                elif args:
                    do_consume(t)
                else:
                    logger.error('%s方法不存在参数: %s' % (str(f), arg_name))

        if len(tags) > 1 and properties.msg_queue_debug:
            print('监听多个标签', tags)

        return queue_args

    return method
