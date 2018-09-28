# coding: utf-8"

"""
配置管理
启动前尝试获得自定义配置(application.py)
无法获取则使用默认配置
"""
import sys
import logging
import os, re, json
from datetime import datetime
from threading import *


def read_self_prop():
    try:
        def_prop = __import__('dophon.def_prop.default_properties', fromlist=True)
        u_prop = __import__('application', fromlist=True)
        # 对比配置文件
        for name in dir(def_prop):
            if re.match('__.*__', name):
                continue
            if name in dir(u_prop):
                continue
            setattr(u_prop, name, getattr(def_prop, name))
        sys.modules['properties'] = u_prop
        sys.modules['dophon.properties'] = u_prop
    except Exception as e:
        logging.error(e)
        sys.modules['properties'] = def_prop
        sys.modules['dophon.properties'] = def_prop
        raise e


try:
    read_self_prop()
except Exception as e:
    logging.error('没有找到自定义配置:(application.py)')
    logging.error('引用默认配置')