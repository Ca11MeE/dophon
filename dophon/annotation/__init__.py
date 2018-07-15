# coding: utf-8
from flask import jsonify, request, abort, render_template, before_render_template
import functools
import sys
from dophon.annotation import AutoWired

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
    'AutoWired'
]

AutoWired = AutoWired


# 响应返回数据修饰器(跳过视图解析器)
# 响应体形式返回
# (自带AutoParam) <------暂未完成
def ResponseBody():
    def method(f):
        @functools.wraps(f)
        def arg(*args, **kwargs):
            result = jsonify(f(*args, **kwargs))
            if result:
                return result
            else:
                return []

        return arg

    return method


# 返回web模板
def ResponseTemplate(template: list):
    """
    返回模板页面
    :param template: 模板页面路径
    :return:
    """

    def method(f):
        def args(*args, **kwargs):
            page_param = f(*args, **kwargs)
            if isinstance(page_param, type({})):
                return render_template(template, **page_param)
            else:
                raise KeyError('页面参数错误!')

        return args

    return method


'''
参数体可以为多个,形参名称必须与请求参数名一一对应(只少不多)
装饰器中关键字参数列表可以指定参数名
'''


# 处理请求参数装饰器(分离参数)
def AutoParam(kwarg_list=[]):
    def method(f):
        @functools.wraps(f)
        def args(*args, **kwargs):
            try:
                if 'GET' == str(request.method):
                    return is_get(f, request, kwarg_list)
                elif 'POST' == str(request.method):
                    return is_post(f, request, kwarg_list)
                else:
                    sys.stderr.write('方法不支持!!')
            except TypeError as t_e:
                sys.stderr.write('参数不匹配!!,msg:' + repr(t_e))
                return abort(500)
            finally:
                sys.stderr.flush()

        return args

    return method


'''
注意!!!
该注解只需方法体内存在一个形参!!!
同样,需要指定参数名的形式参数列表条目也只能存在一个,多个会默认取第一个
不匹配会打印异常
参数以json形式赋值
'''


# 处理请求参数装饰器(统一参数,参数体内参数指向json串)
def FullParam(kwarg_list=[]):
    def method(f):
        @functools.wraps(f)
        def args(*args, **kwargs):
            try:
                if 'POST' == str(request.method) and 'application/json' == request.content_type:
                    r_arg = ()
                    r_kwarg = {}
                    if not kwarg_list:
                        r_arg = (request.json,)
                    else:
                        r_kwarg[kwarg_list[0]] = request.json
                    return f(*r_arg, **r_kwarg)
                else:
                    sys.stderr.write('方法不支持!!')
                    return abort(400)
            except TypeError as t_e:
                sys.stderr.write('参数不匹配!!,msg:' + repr(t_e))
                return abort(500)

        return args

    return method


# 路径绑定装饰器
# 默认服务器从boot获取
def RequestMapping(app, path, methods):
    def method(f):
        result = app.route(path, methods=methods)(f)

        def args(*args, **kwargs):
            return result(*args, **kwargs)

        return args

    return method


def is_get(f, r, kw_list):
    r_arg = ()
    r_kwarg = {}
    if not kw_list:
        r_arg = r.args.to_dict().values()
    else:
        for index in range(len(kw_list)):
            r_kwarg[kw_list[index]] = r.args[kw_list[index]]
    return f(*r_arg, **r_kwarg)


def is_post(f, r, kw_list):
    r_arg = ()
    r_kwarg = {}
    if r.is_json:
        if not kw_list:
            r_arg = is_json(r.json)
        else:
            for index in range(len(kw_list)):
                r_kwarg[kw_list[index]] = r.json[kw_list[index]]
    else:
        if not kw_list:
            r_arg = is_form(r.form)
        else:
            for index in range(len(kw_list)):
                r_kwarg[kw_list[index]] = r.form[kw_list[index]]
    return f(*r_arg, **r_kwarg)


def is_json(arg_list):
    return arg_list.values()


def is_form(arg_list):
    return arg_list.to_dict().values()
