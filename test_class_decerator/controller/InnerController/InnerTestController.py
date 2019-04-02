from dophon.annotation import *
from ..BaseController import BaseController


@DefBean
class InnerBeanController(BaseController):

    def call_method(self):
        return 'this is InnerBeanController'


@DefBean
class InnerBeanController2(BaseController):

    def call_method(self):
        return 'this is InnerBeanController2'


@DefBean
class DefAliasInnerBeanController:
    __bean_alias = 'AliasInnerBeanController'

    def call_method(self):
        return 'this is AliasInnerBeanController,depends on DefAliasInnerBeanController'
