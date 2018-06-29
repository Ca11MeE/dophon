# coding: utf-8
import dophon
from dophon import annotation

_DemoRou=None

app=dophon.blue_print(inject_config={
    'inj_obj_list': {
        '_DemoRou': 'test'
    },
    'global_obj': globals()
},
name='demo',
import_name=__name__)

@annotation.RequestMapping(app=app,path='/',methods=['get'])
@annotation.ResponseBody()
def test():
    return {'hahahah':'测试成功'}