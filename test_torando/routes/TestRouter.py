from dophon.annotation import *


@Get
@Desc()
def test(test_arg1:str='666'):
    return 'this is torando test'
