from dophon.annotation import *
from dophon import properties


@GetRoute('/config/get')
@ResponseBody()
def get_config():
    print(properties.error_info)
    return {
        'host': '127.0.0.1',
        'port': 10010,
        'error_info': 'JSON'
    }


@GetRoute('/raise/500')
@ResponseBody()
def raise_500():
    1 / 0
    return
