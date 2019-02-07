# coding: utf-8
from dophon.annotation import AutoWired
from dophon.annotation import res, req
from dophon.annotation.AutoWired import *

"""
注解集合(部分)
author:CallMeE
date:2018-06-01


"""
__all__ = [
    'ResponseBody',
    'ResponseTemplate',
    'AutoParam',
    'FullParam',
    'RequestMapping',
    'GetRoute',
    'PostRoute',
    'AutoWired',
    'AsResBody',
    'AsResTemp',
    'AsArgs',
    'AsJson',
    'AsFile',
    'BeanConfig',
    'bean',
    'Bean'
]

AutoWired = AutoWired

ResponseBody = AsResBody = res.response_body

ResponseTemplate = AsResTemp = res.response_template

AutoParam = AsArgs = req.auto_param

FullParam = AsJson = req.full_param

FileParam = AsFile = req.file_param

BeanConfig = AutoWired.BeanConfig

bean = AutoWired.bean

Bean = AutoWired.Bean


# 路径绑定装饰器
# 默认服务器从boot获取
def RequestMapping(path='', methods=[], app=None):
    def method(f):
        try:
            # 自动获取蓝图实例并进行http协议绑定
            current_package = __import__(str(getattr(f, "__module__")), fromlist=True)
            # package_app = __import__('dophon.boot', fromlist=True).app \
            package_app = __import__('dophon').blue_print(f"_annotation_auto_reg{getattr(current_package, '__name__')}",
                                                          getattr(current_package, '__name__')) \
                if not hasattr(current_package, '__app') \
                else getattr(current_package, '__app') \
                if not hasattr(current_package, 'app') \
                else current_package.app \
                if not hasattr(app, 'route') \
                else app \
                if not app \
                else __import__('dophon.boot', fromlist=True).app
            # 回设内部蓝图参数
            # print(package_app)
            setattr(current_package, '__app', package_app)
            result = package_app.route(path, methods=methods)(f)
        except Exception as e:
            logger.error(f'{getattr(f, "__module__")}参数配置缺失,请检查({path},{methods},{package_app})')

        def m_args(*args, **kwargs):
            return result(*args, **kwargs)

        return m_args

    return method


# get方法缩写
def GetRoute(path=''):
    def method(f):
        result = RequestMapping(path, ['get'])(f)

        def m_args(*args, **kwargs):
            return result(*args, **kwargs)

        return m_args

    return method


# post方法缩写
def PostRoute(path=''):
    def method(f):
        result = RequestMapping(path, ['post'])(f)

        def args(*args, **kwargs):
            return result(*args, **kwargs)

        return args

    return method
