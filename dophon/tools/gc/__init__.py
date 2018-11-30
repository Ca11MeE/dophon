import gc

gc.enable()  # 开启gc


def show_gc_leak(method):
    """
    打印并获取gc信息
    1.不可达对象统计
    2.不可回收对象统计
    :param method: 打印函数引用
    :return:
    """
    _unreachable = gc.collect()
    method(
        '%s, %s, %s, %s, %s' %
        (
            "unreachable object num: %d" % (_unreachable,),
            "garbage object num: %d" % (len(gc.garbage)),
            "gc object num: %d" % (len(gc.get_objects())),
            "gc threshold num: %d" % (len(gc.get_threshold())),
            "gc stats num: %d" % (len(gc.get_stats())),
        )
    )
    return {
        'unreachable object num': _unreachable,
        'garbage object num': len(gc.garbage),
        "gc object num": len(gc.get_objects()),
        # "gc object info": gc.get_objects(),
        "gc threshold num": len(gc.get_threshold()),
        "gc threshold info": str(gc.get_threshold()),
        "gc stats num": len(gc.get_stats()),
        "gc stats info": str(gc.get_stats()),
    }
