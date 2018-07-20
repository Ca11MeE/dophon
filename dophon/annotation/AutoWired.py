# coding: utf-8
# 自动注入修饰器
import sys
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
                if obj_name in globals():
                    g[obj_name] = globals()[obj_name]
                else:
                    instance = clz[index]()
                    globals()[obj_name] = instance
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
                    if obj_name in globals():
                        g[obj_name] = globals()[obj_name]
                    else:
                        instance = clz[index]()
                        globals()[obj_name] = instance
                        g[obj_name] = instance
                except Exception as e:
                    logger.error('注入' + str(a_name[index]) + '失败,原因:' + str(e) + '\n')
                    continue
            return f()

        return inner_function

    return wn
