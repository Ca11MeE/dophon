from dophon.msg_queue import MsgCenter
from dophon import logger
from dophon import properties

logger.inject_logger(globals())

center = MsgCenter.get_center(remote_center=properties.mq.get('remote_center', False))


def local_producer(tag, delay: int = 0):
    def method(f):
        def single_tag(*args, **kwargs) -> dict:
            center.write_p_book(tag)
            # 执行被装饰方法,检查返回值
            result = f(*args, **kwargs)
            p_result = center.do_send(result, tag, delay)
            return p_result

        def multi_tag(*args, **kwargs) -> dict:
            p_result_list = []
            for inner_tag in tag:
                center.write_p_book(inner_tag)
                # 执行被装饰方法,检查返回值
                result = f(*args, **kwargs)
                p_result_list.append(center.do_send(result, inner_tag, delay))
            return p_result_list

        def unsupport_tag(*args, **kwargs) -> dict:
            logger.warning('不支持的标签类型! %s' % (args, kwargs))

        r_method = single_tag if isinstance(tag, str) \
            else multi_tag if isinstance(tag, list) \
            else unsupport_tag

        return r_method

    return method


def remote_producer(tag, delay: int = 0):
    return


producer = local_producer
