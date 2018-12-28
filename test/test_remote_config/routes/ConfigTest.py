from dophon import blue_print
from dophon.annotation import *
from dophon import properties

app = blue_print(
    name='config_test',
    import_name=__name__
)


@RequestMapping(app, '/config/get', ['get'])
@ResponseBody()
def get_config():
    print(properties.error_info)
    return {
        'host': '127.0.0.1',
        'port': 10010,
        'error_info': 'JSON'
    }

@RequestMapping(app,'/raise/500',['get'])
@ResponseBody()
def raise_500():
    1 / 0
    return