from dophon.annotation import *


@GetRoute('/test/dese')
@Desc()
@ResponseBody()
def test_desc_decr(test_arg = 'test args'):
    """
    this is test for description decoration
    :param test_arg:
    :return:
    """
    print(f'this.is decr {test_arg}')
    return {}


@Get
@ResponseBody()
@Desc()
def test_desc_with_no_default(test_arg):
    """
    this is test for description decoration without default parm value
    :param test_arg:
    :return:
    """
    print('this.is decr without any default value')
    return {}


@Get
@ResponseBody()
@Desc()
def test_multiple_param(arg_1:str,arg_2:int=666,arg_3:dict={},arg_4:tuple=('a',1,object()),arg_5:list=[1,2,3,4,5,6]):
    """
    this is test_multiple_param

    :param arg_1:
    :param arg_2:
    :param arg_3:
    :param arg_4:
    :param arg_5:
    :return:
    """
    return {}