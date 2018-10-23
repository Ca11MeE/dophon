from dophon.msg_queue import MsgCenter
from dophon import logger
from dophon import properties

logger.inject_logger(globals())

center = MsgCenter.get_center(remote_center=properties.mq.get('remote_center',False))


def producer(tag, delay: int = 0):
    def method(f):
        def single_tag(*args, **kwargs) -> dict:
            center.write_p_book(tag)
            # 执行被装饰方法,检查返回值
            result = f(*args, **kwargs)
            center.do_send(result, tag, delay)

        def multi_tag(*args, **kwargs) -> dict:
            for inner_tag in tag:
                center.write_p_book(inner_tag)
                # 执行被装饰方法,检查返回值
                result = f(*args, **kwargs)
                center.do_send(result, inner_tag, delay)

        def unsupport_tag(*args, **kwargs) -> dict:
            logger.warning('不支持的标签类型! %s' % (args, kwargs))

        r_method=single_tag if isinstance(tag, str) \
            else multi_tag if isinstance(tag, list) \
            else unsupport_tag

        return r_method

    return method
