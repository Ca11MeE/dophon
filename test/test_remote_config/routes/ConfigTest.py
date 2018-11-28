from dophon import blue_print
from dophon.annotation import *

app = blue_print(
    name='config_test',
    import_name=__name__
)


@RequestMapping(app, '/config/get', ['get'])
@ResponseBody()
def get_config():
    return {
        'host': '127.0.0.1',
        'port': 10010
    }
