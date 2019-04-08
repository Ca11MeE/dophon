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
