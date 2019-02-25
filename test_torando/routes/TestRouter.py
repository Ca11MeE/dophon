from dophon.annotation import *


@Get
@Desc()
def test(test_arg1:str='666'):
    """
    test doc
    :param test_arg1:
    :return:
    """
    return 'this is torando test'
