from dophon.annotation import *
from .BaseController import BaseController


@DefBean
class DefBean(BaseController):
    def call_method(self):
        return 'this is DefBean'
