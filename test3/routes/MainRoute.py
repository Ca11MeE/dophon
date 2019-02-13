from dophon import *
from dophon.annotation import *


app = blue_print('main', __name__,url_prefix='/main')


@RequestMapping('/', ['get'])
@ResponseTemplate(['index.html'])
def index():
    return {}


@GetRoute('/get')
@ResponseTemplate(['index.html'])
def get_index():
    return {}


@PostRoute('/post')
@ResponseTemplate(['index.html'])
def post_index():
    return {}


@Get
@ResponseTemplate(['index.html'])
def test_get():
    return {}
