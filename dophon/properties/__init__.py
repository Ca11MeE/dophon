# coding: utf-8

"""
配置管理
启动前尝试获得自定义配置(application.py)
无法获取则使用默认配置
"""
import sys
import logging
import re
import os
from . import properties_handler
from urllib3 import PoolManager

logger = logging.Logger(name=__name__)

re_import_prop_flag = False

properties_file_name_list = ['application.yml', 'application.yml', 'application.properties', 'application.prop',
                             'application.xml', 'application.py']

properties_file_handler = {
    'py': properties_handler.py_handler,
    'yml': properties_handler.yml_handler,  # yml格式模块文件
    'yaml': properties_handler.yml_handler,  # yml格式模块文件
    'properties': properties_handler.properties_handler,  # yml格式模块文件
    'prop': properties_handler.properties_handler,  # yml格式模块文件
    'xml': properties_handler.xml_handler  # xml格式模块文件
}


def read_self_prop():
    global re_import_prop_flag
    try:
        def_prop = __import__('dophon.def_prop.__init__', fromlist=True)
        u_prop = __import__('application', fromlist=True)
        # 对比配置文件
        for name in dir(def_prop):
            if re.match('__.*__', name):
                continue
            if name in dir(u_prop):
                continue
            setattr(u_prop, name, getattr(def_prop, name))
        # 校验远程配置
        if hasattr(u_prop, 'remote_prop'):
            try:
                url = getattr(u_prop, 'remote_prop')
                pool = PoolManager()
                res = pool.request('get',url)
                print(res.data)
            except Exception as inner_e:
                print(inner_e)
        sys.modules['properties'] = u_prop
        sys.modules['dophon.properties'] = u_prop
    except Exception as e:
        get_properties = False
        # 添加项目路径到环境变量
        print('添加项目路径到环境变量: %s' % (os.getcwd(),))
        for (root, dirs, files) in os.walk(os.getcwd(), topdown=True):
            if get_properties:
                break
            for prop_file_name in properties_file_name_list:
                if get_properties:
                    break
                if prop_file_name in files:
                    file_info = prop_file_name.split('.')
                    file_name = file_info[0]
                    file_type = file_info[1]
                    if file_type in properties_file_handler:
                        properties_file_handler[file_type](root, prop_file_name, file_name, file_type)
                        print('读取配置: %s%s%s' % (root, os.sep, prop_file_name,))
                        sys.path.append(root)
                    else:
                        logger.error('无法读取的配置文件类型(%s)' % (file_type,))
                    get_properties = True
        if not re_import_prop_flag:
            logger.info('重新引入配置')
            re_import_prop_flag = True
            read_self_prop()
        else:
            logger.warning('重新引入配置失败')
            sys.modules['properties'] = def_prop
            sys.modules['dophon.properties'] = def_prop
            raise e


try:
    read_self_prop()
except Exception as e:
    logger.error(e)
    logger.error('没有找到自定义配置:(application.py)')
    logger.error('引用默认配置')
    logger.info('创建配置文件: application.py')
    def_prop = __import__('dophon.def_prop.default_properties', fromlist=True)
    with open(os.getcwd() + os.sep + 'application.py', 'wb') as app_prop:
        for name in dir(def_prop):
            if re.match('__.*__', name):
                continue
            else:
                value = getattr(def_prop, name)
                if type(value) is type(os):
                    continue
                app_prop.write(
                    bytes(name + '=' + re.sub('\\\\', '/',
                                              str(('\'' + value + '\'') if isinstance(value, str) else value)) + '\n',
                          encoding='utf-8'))
    read_self_prop()
