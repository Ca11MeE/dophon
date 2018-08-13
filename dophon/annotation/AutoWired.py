# coding: utf-8
# 自动注入修饰器
import re
import inspect
from dophon import logger

"""
自动注入注解

ps:默认为单例模式,利用模块局内变量域管理实例,减少内存冗余

author:CallMeE
date:2018-06-01

实现自动注入功能需在蓝图模块(也可以在其他位置)中定义方法(inject_obj)并添加下列两个注解之一
DEMO;
# 注入对象
@AutoWired.InnerWired([ShopGoodsController.ShopGoodsController],a_w_list=['_SGCobj'],g=globals())
或者
@AutoWired.OuterWired(obj_list,g=globals())
def inject_obj():
    pass
调用inject_obj()即可实现自动注入
注意:
1.a_w_list中的元素为注入引用名,必须要与注入目标引用名一致,否则注入失效
2.注入位置必须显式定义一个值为None的引用,否则编译不通过
3.注入类型必须为可初始化类型(定义__new__ or __init__)
"""

logger.inject_logger(globals())

obj_manager = {}


class UniqueError(Exception):
    """
    唯一错误,存在覆盖已存在的别名实例
    """


# 显式参数注入
def InnerWired(clz, g, a_w_list=[]):
    # print(locals())
    # 注入实例
    def wn(f):
        def inner_function(*args, **dic_args):
            # 获取数组
            if a_w_list and 0 < len(a_w_list):
                # 装饰器参数查找赋值
                a_name = a_w_list
            else:
                if dic_args['a_w_list'] and 0 < dic_args['a_w_list']:
                    # 被装饰函数关键字参数查找赋值
                    a_name = dic_args['a_w_list']
                else:
                    if not args:
                        logger.error('动态形参为空')
                        raise Exception('动态形参为空!!')
                    # 被装饰函数位置参数查找赋值
                    a_name = args[0]
            for index in range(len(a_name)):
                logger.info(str(a_name[index]) + " 注入 " + str(clz[index]))
                obj_name = a_name[index]
                if obj_name in obj_manager:
                    g[obj_name] = obj_manager[obj_name]
                else:
                    instance = clz[index]()
                    obj_manager[obj_name] = instance
                    g[obj_name] = instance
            # return arg
            return f()

        return inner_function

    return wn


# 自定义参数列表注入
def OuterWired(obj_obj, g):
    # 前期准备
    clz = []
    a_w_list = []
    for key in obj_obj.keys():
        a_w_list.append(key)
        clz.append(obj_obj[key])

    # 注入实例
    def wn(f):
        logger.info('开始注入实例')

        def inner_function(*args, **dic_args):
            # 获取数组
            if a_w_list and 0 < len(a_w_list):
                # 装饰器参数查找赋值
                a_name = a_w_list
            else:
                if dic_args['a_w_list']:
                    # 被装饰函数关键字参数查找赋值
                    a_name = dic_args['a_w_list']
                else:
                    if not args:
                        logger.error('动态形参为空!!')
                        raise Exception('动态形参为空!!')
                    # 被装饰函数位置参数查找赋值
                    a_name = args[0]
            for index in range(len(a_name)):
                logger.info(str(a_name[index]) + " 注入 " + str(clz[index]))
                try:
                    obj_name = a_name[index]
                    if obj_name in obj_manager:
                        g[obj_name] = obj_manager[obj_name]
                    else:
                        instance = clz[index]()
                        obj_manager[obj_name] = instance
                        g[obj_name] = instance
                except Exception as e:
                    logger.error('注入' + str(a_name[index]) + '失败,原因:' + str(e))
                    continue
            return f()

        return inner_function

    return wn


"""
2018-07-22

参照spring实例管理实现实例管理
1.bean装饰器
    参照spring中bean注解
    需执行被装饰方法才能交由实例管理器管理
    默认使用方法名作为实例管理名
    可传入自定义别名替换别名
    同名别名会抛出二义性错误
    暂不支持lambda表达式(强制调用非装饰器装饰lambda表达式会产生注册实例无效)
2.BeanConfig实例管理器
    定义管理器子类后定义bean装饰方法后实例化一次后全部交由全局实例管理管理实例
    支持with语法
3.Bean实例获取类
    实例获取需传入实例别名或实例类型
    可直接赋值变量
"""


def bean(name: str = None):
    """
    向实例管理器插入实例
    :param by_name: 别名(不传值默认为类型)
    :return:
    """

    def method(f):
        def args(*args, **kwargs):
            result = f(*args, **kwargs)
            if result is None:
                raise TypeError('无法注册实例:' + str(result))
            if name:
                if name in obj_manager:
                    raise UniqueError('存在已注册的实例:' + name)
                obj_manager[name] = result
            else:
                alias_name = getattr(f, '__name__') if getattr(f, '__name__') else getattr(type(result), '__name__')
                if alias_name in obj_manager:
                    raise UniqueError('存在已注册的实例')
                else:
                    obj_manager[alias_name] = result
            return

        return args

    return method


class BeanConfig:
    """
    实力配置类,类内自定义方法带上bean注解即可(参照springboot中been定义)
    """

    def __call__(self, *args, **kwargs):
        for name in dir(self):
            if re.match('__.+__', name):
                continue
            attr = getattr(self, name)
            if callable(attr):
                fields = inspect.getfullargspec(attr).args
                staticmethod(attr(*fields))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and exc_val and exc_tb:
            logger.error('%s 实例不存在', str(exc_val))
        pass

    def __init__(self):
        logger.info('执行批量实例管理初始化')
        self()


class Bean:
    def __new__(cls, *args, **kwargs):
        if args or len(args) > 1:
            bean_key = args[0]
        elif kwargs or len(kwargs) > 1:
            bean_key = kwargs.keys()[0]
        else:
            raise KeyError('不存在实例别名或实例类型')
        if isinstance(bean_key, str):
            if bean_key in obj_manager:
                return obj_manager[bean_key]
            raise KeyError('不存在该别名实例')
        elif isinstance(bean_key, type):
            type_list = []
            for key in obj_manager.keys():
                if re.match('__.+__', key):
                    continue
                bean_obj = obj_manager[key]
                if isinstance(bean_obj, bean_key):
                    if len(type_list) > 0:
                        raise UniqueError('存在定义模糊的实例获取类型')
                    type_list.append(bean_obj)
            if not type_list:
                raise KeyError('不存在该类型实例')
            return type_list[0]
