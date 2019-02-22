from functools import wraps
from ..req import auto_param
from inspect import getfullargspec

DESC_INFO = {}

PATH_TRANSLATE_DICT = {}


def desc():
    """
    函数描述装饰器
    自动添加请求属性配对
    :return:
    """

    def inner_method(f):
        # 获取方法的参数名集合
        # FullArgSpec(args=['test_arg1'], varargs=None, varkw=None, defaults=None, kwonlyargs=[], kwonlydefaults=None, annotations={})
        full_arg_spec = getfullargspec(f)
        __args = full_arg_spec.args
        __defaults = full_arg_spec.defaults
        __annotations = full_arg_spec.annotations
        # print(full_arg_spec)
        # 处理参数信息,放入参数信息列
        __function_arg_info = {}
        for __inner_arg_index in range(len(__args)):
            __function_arg_info[__args[__inner_arg_index]] = {
                'name': __args[__inner_arg_index],
                'default_value': __defaults[__inner_arg_index],
                'annotation_type': __annotations[__args[__inner_arg_index]]
            }
        DESC_INFO[f'{getattr(f, "__module__")}.{getattr(f, "__name__")}'] = __function_arg_info

        @wraps(f)
        def inner_args(*args, **kwargs):
            return auto_param()(f)(*args, **kwargs)

        return inner_args

    return inner_method
