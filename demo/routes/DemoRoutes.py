# coding: utf-8
import dophon
from dophon.annotation import *
from demo.controller.controller import TestController

_DemoRou = None

app = dophon.blue_print(inject_config={
    'inj_obj_list': {
        '_DemoRou': TestController
    },
    'global_obj': globals()
},
    name='demo',
    import_name=__name__,
    template_folder='../templates')


@RequestMapping(app=app, path='/', methods=['get'])
@ResponseBody()
def test():
    print(id(app))
    return {'hahahah': '测试成功'}


@RequestMapping(app=app, path='/index', methods=['get'])
@ResponseTemplate(template=['index.html'])
def index():
    return {}


@RequestMapping(app, '/exc/500', ['get', 'post'])
def demo_exception():
    1 / 0


@RequestMapping(app, '/get/bean/1', ['get'])
def bean_1():
    b = Bean('call_beans')
    b.call()
    pass


@RequestMapping(app, '/get/bean/2', ['get'])
def bean_2():
    b = Bean('call_beans')
    b.call()
    pass


@RequestMapping(app, '/test/page/select', ['get'])
@ResponseBody()
def test_page_select():
    result = _DemoRou.test_page_select()
    return result


@RequestMapping(app, '/test/page/unselect', ['get'])
@ResponseBody()
def test_page_unselect():
    result = _DemoRou.test_page_unselect()
    return result


@RequestMapping(app, '/test/like/sql', ['get'])
@ResponseBody()
def test_like_sql():
    result = _DemoRou.test_like_sql()
    return result
