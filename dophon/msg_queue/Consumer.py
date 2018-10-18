from dophon import logger
from dophon import properties
from dophon.msg_queue import MsgCenter

center = MsgCenter.get_center()

logger.inject_logger(globals())


def consumer(tag: str, delay: int = 0, retry: int = 3, as_args: bool = False):
    tags = tag if isinstance(tag, list) else tag.split('|')

    def method(f):
        def queue_args(*args, **kwargs):
            def args(tt, *args, **kwargs):
                center.do_get(tt)

            for t in tags:
                # 执行消息中心信息监听
                args(t)

        if len(tags) > 1 and properties.msg_queue_debug:
            print('监听多个标签', tags)

        return queue_args

    return method
