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

re_import_prop_flag = False


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
        sys.modules['properties'] = u_prop
        sys.modules['dophon.properties'] = u_prop
    except Exception as e:
        # 添加项目路径到环境变量
        logging.info('添加项目路径到环境变量: %s' % (os.getcwd(),))
        for (root, dirs, files) in os.walk(os.getcwd(), topdown=True):
            if 'application.py' in files:
                sys.path.append(root)
                break
        if not re_import_prop_flag:
            logging.info('重新引入配置')
            re_import_prop_flag = True
            read_self_prop()
        else:
            logging.warning('重新引入配置失败')
            sys.modules['properties'] = def_prop
            sys.modules['dophon.properties'] = def_prop
            raise e


try:
    read_self_prop()
except Exception as e:
    logging.error('没有找到自定义配置:(application.py)')
    logging.error('引用默认配置')
    logging.info('创建配置文件: application.py')
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
