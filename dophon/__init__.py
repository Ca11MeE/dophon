# coding: utf-8
from flask import Blueprint

from dophon.tools.dynamic_import import d_import

name = 'dophon'


def blue_print(name, import_name, inject_config: dict = {}, static_folder=None,
               static_url_path=None, template_folder=None,
               url_prefix=None, subdomain=None, url_defaults=None,
               root_path=None):
    """
    获取Flask路由,同时实现自动注入(可细粒度管理)
    :param inject_config:注入配置,类型为dict
    :param name:同Blueprint.name
    :param import_name:同Blueprint.import_name
    :param static_folder:同Blueprint.static_floder
    :param static_url_path:同Blueprint.static_url_path
    :param template_folder:同Blueprint.template_folder
    :param url_prefix:同Blueprint.url_prefix
    :param subdomain:同Blueprint.subdomain
    :param url_defaults:同Blueprint.url_defaults
    :param root_path:同Blueprint.root_path
    :return:
    """
    blue_print_obj = Blueprint(name=name, import_name=import_name, static_folder=static_folder,
                               static_url_path=static_url_path, template_folder=template_folder,
                               url_prefix=url_prefix, subdomain=subdomain, url_defaults=url_defaults,
                               root_path=root_path)
    if inject_config:
        autowire = __import__('dophon.annotation.AutoWired', fromlist=True)
        outerwired = getattr(autowire, 'OuterWired')
        outerwired(
            obj_obj=inject_config['inj_obj_list'],
            g=inject_config['global_obj']
        )(inject)()
    return blue_print_obj


def inject():
    """
    用于构造注入入口,无意义
    :return:
    """
    pass


def dophon_boot(f):
    """
    装饰器形式启动
    :return:
    """

    def arg(*args, **kwargs):
        from . import tools
        if tools.is_not_windows():
            d_import('gevent')
            from gevent import monkey
            monkey.patch_all()
        boot = __import__('dophon.boot', fromlist=True)
        kwargs['boot'] = boot
        return f(*args, **kwargs)

    return arg

__all__ = ['BluePrint', 'blue_print']

BluePrint = blue_print
