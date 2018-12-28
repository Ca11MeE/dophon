# from dophon_properties import *
#
# get_properties(DOPHON)
from dophon_logger import *

"""
框架其余功能装饰器
"""
logger = get_logger(DOPHON)

logger.inject_logger(globals())


def logger_execute(*args, **kwargs):
    logger.info(f'{args} : {kwargs}')


def log_router(func=logger_execute):
    # 执行路由日志记录
    func()

    def r_method(f):
        def r_args(*args, **kwargs):
            f(*args, **kwargs)

        return r_args

    return r_method


def logs():
    print('logs!!!')


@log_router()
def test():
    print('ooo')


test()
