from dophon import logger
from dophon import properties
import os, sys
import xml.dom.minidom as dom

logger.inject_logger(globals())

name_sep = '_'

modules_list = []


def check_modules():
    """
    加载框架配置模块
    :return:
    """
    logger.info('校验模块')
    modules_path = properties.project_root + '/module.xml'
    if os.path.exists(modules_path):
        with open(modules_path) as modules_file:
            modules_tree = dom.parse(modules_file)
            # print(modules_tree)
            modules_info = modules_tree.getElementsByTagName('module')
            # print(modules_info)
            for module_info in modules_info:
                pre_name = module_info.getElementsByTagName('pre-name')
                pre_name = pre_name[0].childNodes[0].data if pre_name and pre_name[0].childNodes else None
                name = module_info.getElementsByTagName('name')
                name = name[0].childNodes[0].data if name and name[0].childNodes else None
                version = module_info.getElementsByTagName('version')
                version = version[0].childNodes[0].data if version and version[0].childNodes else None
                module_name = ((pre_name + name_sep) if pre_name else '') + name
                module_code_str = ((pre_name + '.') if pre_name else '') + name
                # 添加模块到模块列表
                modules_list.append(module_code_str)
                while True:
                    try:
                        # 校验模块安装
                        module = __import__(module_name)
                        # 等待模块安装完成
                        sys.modules[module_code_str] = module
                        break
                    except Exception as e:
                        # print(e)
                        logger.info('install %s >=%s' % (module_name, version if version else 'release',))
                        # 利用pip模块安装所需模块
                        pip_arg_list = ['install',
                                        module_name + (('>=' + version) if version else ''),
                                        '--user']
                        if not version:
                            pip_arg_list.append('-U')
                        from pip import __main__ as pip_main
                        pip_main._main(pip_arg_list)