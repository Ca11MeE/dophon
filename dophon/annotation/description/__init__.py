from functools import wraps
from ..req import auto_param
from inspect import getfullargspec

DESC_INFO = {}

PATH_TRANSLATE_DICT = {}


def desc(

):
    """
    函数描述装饰器
    自动添加请求属性配对
    :return:
    """

    def inner_method(f):
        # 获取方法的参数名集合
        # FullArgSpec(args=['test_arg1'], varargs=None, varkw=None, defaults=None, kwonlyargs=[], kwonlydefaults=None, annotations={})
        full_arg_spec = getfullargspec(f)
        __own_doc = getattr(f, '__doc__')  # 自身定义的文档
        __args = full_arg_spec.args  # 通过函数定义的属性名集合
        __defaults = full_arg_spec.defaults  # 通过函数定义参数默认值
        __annotations = full_arg_spec.annotations  # 通过函数定义的参数修饰
        # print(full_arg_spec)
        # 处理参数信息,放入参数信息列
        __function_arg_info = {}
        for __inner_arg_index in range(len(__args)):
            __function_arg_info[__args[__inner_arg_index]] = {
                'name': __args[__inner_arg_index],
                'default_value': __defaults[__inner_arg_index],
                'annotation_type': __annotations[__args[__inner_arg_index]],
                'own_doc': __own_doc
            }
        DESC_INFO[f'{getattr(f, "__module__")}.{getattr(f, "__name__")}'] = __function_arg_info

        @wraps(f)
        def inner_args(*args, **kwargs):
            return auto_param()(f)(*args, **kwargs)

        return inner_args

    return inner_method
