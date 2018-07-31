# coding: utf-8
import dophon
from dophon.annotation import *
from demo.controller.controller import TestController

_DemoRou=None

app=dophon.blue_print(inject_config={
    'inj_obj_list': {
        '_DemoRou': TestController
    },
    'global_obj': globals()
},
name='demo',
import_name=__name__,
template_folder='../templates')

@RequestMapping(app=app,path='/',methods=['get'])
@ResponseBody()
def test():
    return {'hahahah':'测试成功'}

@RequestMapping(app=app,path='/index',methods=['get'])
@ResponseTemplate(template=['index.html'])
def index():
    return {}