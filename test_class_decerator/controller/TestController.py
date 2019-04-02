from dophon.annotation import *
from .BaseController import BaseController


@DefBean
class TestController(BaseController):
    def call_method(self):
        return 'this is TestController'


@DefBean
class TestController2(BaseController):
    def call_method(self):
        return 'this is TestController2'
