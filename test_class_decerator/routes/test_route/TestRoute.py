from dophon.annotation import *

@Get
@ResponseBody()
def test():
    def_bean = Bean('def_bean')
    print(def_bean)
    test_controller = Bean('test_controller')
    print(test_controller)
    test_controller2 = Bean('test_controller2')
    print(test_controller2)
    inner_bean_controller = Bean('inner_bean_controller')
    print(inner_bean_controller)
    inner_bean_controller2 = Bean('inner_bean_controller2')
    print(inner_bean_controller2)
    alias_inner_bean_controller = Bean('alias_inner_bean_controller')
    print(alias_inner_bean_controller)
    print('hallo')
    return {
        'def_bean':def_bean.call_method(),
        'test_controller':test_controller.call_method(),
        'test_controller2':test_controller2.call_method(),
        'inner_bean_controller':inner_bean_controller.call_method(),
        'inner_bean_controller2':inner_bean_controller2.call_method(),
        'alias_inner_bean_controller':alias_inner_bean_controller.call_method(),
    }