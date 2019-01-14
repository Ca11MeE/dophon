from dophon import blue_print
from dophon.annotation import *

app = blue_print('main', __name__)


@RequestMapping(app, '/', ['get'])
@ResponseTemplate(['index.html'])
def index():
    return {}
