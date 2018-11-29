# -*- coding:utf-8 -*-
import yaml
import os
from xml.parsers.expat import ParserCreate

# yml文件格式后缀
yml_file_type = ['yml', 'yaml']
# properties 文件格式后缀
properties_file_type = ['properties', 'prop']
# xml 文件格式后缀
xml_file_type = ['xml']

# 配置文件基本标识
base_prop_key = [
    'project_root',
    'server_threaded',
    'server_gevented',
    'server_processes',
    'debug_trace',
    'ip_count',
    'host',
    'port',
    'ssl_context',
    'blueprint_path',
    'pool_conn_num',
    'pydc_host',
    'pydc_port',
    'pydc_user',
    'pydc_password',
    'pydc_database',
    'pydc_xmlupdate_sech',
    'db_pool_exe_time',
    'msg_queue_max_num',
    'msg_queue_debug',
    'mq',
    'logger_config',
    'error_info'
]
# 额外配置标识
extra_prop_key = ['remote_prop']


class Properties(object):
    """
    properties / prop 文件反序列类
    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.properties = {}

    def __getDict(self, strName, dictName, value):

        if (strName.find('.') > 0):
            k = strName.split('.')[0]
            dictName.setdefault(k, {})
            return self.__getDict(strName[len(k) + 1:], dictName[k], value)
        else:
            try:
                dictName[strName] = int(value)
            except:
                try:
                    dictName[strName] = eval(value)
                except:
                    dictName[strName] = value
            return

    def get_properties(self):
        try:
            pro_file = open(self.file_path, 'Ur')
            for line in pro_file.readlines():
                line = line.strip().replace('\n', '')
                if line.find("#") != -1:
                    line = line[0:line.find('#')]
                if line.find('=') > 0:
                    strs = line.split('=')
                    strs[1] = line[len(strs[0]) + 1:]
                    self.__getDict(strs[0].strip(), self.properties, strs[1].strip())
        except Exception as e:
            raise e
        else:
            pro_file.close()
        return self.properties


class Xml:
    """
    xml文件反序列类
    """
    LIST_TAGS = ['COMMANDS']

    def __init__(self, data=None):
        self._parser = ParserCreate()
        self._parser.StartElementHandler = self.start
        self._parser.EndElementHandler = self.end
        self._parser.CharacterDataHandler = self.data
        self.result = {}
        if data:
            self.feed(data)
            self.close()

    def feed(self, data):
        self._stack = []
        self._data = ''
        self._parser.Parse(data, 0)

    def close(self):
        self._parser.Parse("", 1)
        del self._parser

    def start(self, tag, attrs):
        assert attrs == {}
        assert self._data.strip() == ''
        self._stack.append([tag])
        self._data = ''

    def end(self, tag):
        last_tag = self._stack.pop()
        assert last_tag[0] == tag
        if len(last_tag) == 1:  # leaf
            data = self._data
        else:
            if tag not in Xml.LIST_TAGS:
                # build a dict, repeating pairs get pushed into lists
                data = {}
                for k, v in last_tag[1:]:
                    try:
                        v = int(v)
                    except:
                        try:
                            v = eval(v)
                        except:
                            v = v
                    if k not in data:
                        data[k] = v
                    else:
                        el = data[k]
                        if type(el) is not list:
                            data[k] = [el, v]
                        else:
                            el.append(v)
            else:  # force into a list
                data = [{k: v} for k, v in last_tag[1:]]
        if self._stack:
            self._stack[-1].append((tag, data))
        else:
            self.result = {tag: data}
        self._data = ''

    def data(self, data):
        self._data = data

    def get_dict(self):
        return self.result


def prop_keys():
    return base_prop_key + extra_prop_key


def translate_to_file(temp_path, file_dict, file_name):
    """
    将其他形式配置文件翻译成py文件
    :param temp_path: 源配置文件路径
    :param file_dict: 配置文件内容字典(dict)
    :param file_name: 配置文件名
    :return:
    """
    with open(temp_path, 'w', encoding='utf-8') as d_prop_f:
        for k, v in file_dict.items():
            if k in prop_keys():
                d_prop_f.write(k + '=' + (('\'' + v + '\'') if isinstance(v, str) else str(v)))
                d_prop_f.write('\n')
    return file_name


def py_handler(root, prop_file_name, file_name, file_type):
    """
    py 文件转换处理
    :return:
    """
    # py文件不作处理
    pass


def yml_handler(root, prop_file_name, file_name, file_type):
    """
    yml文件转换处理
    :return:
    """
    if file_type in yml_file_type:
        with open(root + os.sep + prop_file_name, 'r', encoding='utf-8') as f:
            file_dict = yaml.load(f)
            temp_path = root + os.sep + 'application.py'
            return translate_to_file(temp_path, file_dict, file_name)
    else:
        raise Exception('不能识别的yml或yaml类型')


def properties_handler(root, prop_file_name, file_name, file_type):
    """
    properties / prop 文件转换处理
    :return:
    """
    if file_type in properties_file_type:
        file_dict = Properties(root + os.sep + prop_file_name).get_properties()
        temp_path = root + os.sep + 'application.py'
        return translate_to_file(temp_path, file_dict, file_name)
    else:
        raise Exception('不能识别的properties或prop类型')


def xml_handler(root, prop_file_name, file_name, file_type):
    """
    xml文件转换处理
    :return:
    """
    with open(root + os.sep + prop_file_name, 'r', encoding='utf-8') as dom:
        file_dict = Xml(dom.read()).get_dict()
        temp_path = root + os.sep + 'application.py'
        return translate_to_file(temp_path, file_dict.get('config'), file_name)
