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
def RequestMapping(app, path, methods):
    def method(f):
        result = app.route(path, methods=methods)(f)

        def args(*args, **kwargs):
            return result(*args, **kwargs)

        return args

    return method
