import functools
from flask import request, abort
from dophon import logger

'''
参数体可以为多个,形参名称必须与请求参数名一一对应(只少不多)
装饰器中关键字参数列表可以指定参数名
'''

logger.inject_logger(globals())

# 处理请求参数装饰器(分离参数)


def auto_param(kwarg_list=[]):
    def method(f):
        @functools.wraps(f)
        def args(*args, **kwargs):
            try:
                if 'GET' == str(request.method):
                    return is_get(f, request, kwarg_list)
                elif 'POST' == str(request.method):
                    return is_post(f, request, kwarg_list)
                else:
                    logger.error('方法不支持!!')
            except TypeError as t_e:
                logger.error('参数不匹配!!,msg:' + repr(t_e))
                raise t_e
                return abort(500)

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
def full_param(kwarg_list=[]):
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
                elif 'GET' == str(request.method):
                    r_arg = ()
                    r_kwarg = {}
                    if not kwarg_list:
                        r_arg = (request.args.to_dict(),)
                    else:
                        r_kwarg[kwarg_list[0]] = request.args.to_dict()
                    return f(*r_arg, **r_kwarg)
                else:
                    logger.error('json统一参数不支持该请求方法!!')
                    return abort(400)
            except TypeError as t_e:
                logger.error('参数不匹配!!,msg:' + repr(t_e))
                return abort(500)

        return args

    return method


def file_param(alias_name: str = 'files', extra_param: str = 'args'):
    """
    文件参数装在装饰器

    ps 文件上传暂时只支持路由方法内单个参数接收(会有校验策略)

    参数demo(小程序):
        ImmutableMultiDict([('img_upload_test', <FileStorage: 'filename' ('image/jpeg')>)])
    :return:
    """

    def method(f):
        @functools.wraps(f)
        def args(*args, **kwargs):
            # 检测参数
            a_nums = len(args) + len(kwargs)
            if a_nums > 0:
                logger.error('路由绑定参数数量异常')
                raise Exception('路由绑定参数数量异常')
            try:
                extra_param_value=(request.form if request.form else request.json).to_dict()
            except:
                extra_param_value={}
            k_args = {
                alias_name: request.files.to_dict(),
                extra_param: extra_param_value
            }
            return f(**k_args)

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
