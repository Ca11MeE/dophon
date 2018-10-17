from dophon.msg_queue import MsgCenter

center = MsgCenter.MsgCenter()


def producer(tag, delay: int = 0):
    # 预注册消息通道
    center.write_p_book(tag)

    def method(f):
        def single_tag(*args, **kwargs) -> dict:
            # 执行被装饰方法,检查返回值
            result = f(*args, **kwargs)
            center.do_send(result, tag, delay)

        def multi_tag(*args, **kwargs) -> dict:
            for inner_tag in tag:
                # 执行被装饰方法,检查返回值
                result = f(*args, **kwargs) + inner_tag
                center.do_send(result, tag, delay)

        if isinstance(tag, str):
            return single_tag
        if isinstance(tag, list):
            return multi_tag

    return method
