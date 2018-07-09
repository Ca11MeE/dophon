from datetime import datetime
import sys
import re

import struct

db_type_python_dict = {
    # 字符串类型
    'char': {
        'type': str,
        'str_name': 'str',
        'min_length': 0,
        'max_length': 255
    },
    'varchar': {
        'type': str,
        'str_name': 'str',
        'min_length': 0,
        'max_length': 65535
    },
    'tinytext': {
        'type': str,
        'str_name': 'str',
        'min_length': 0,
        'max_length': 255
    },
    'text': {
        'type': str,
        'str_name': 'str',
        'min_length': 0,
        'max_length': 65535
    },
    'mediumtext': {
        'type': str,
        'str_name': 'str',
        'min_length': 0,
        'max_length': 16777215
    },
    'longtext': {
        'type': str,
        'str_name': 'str',
        'min_length': 0,
        'max_length': 4294967295
    },
    'enum': {
        'type': tuple,
        'str_name': 'tuple',
        'min_length': 0,
        'max_length': 65535 * 2
    },
    'set': {
        'type': set,
        'str_name': 'set',
        'min_length': 0,
        'max_length': 64 * 8
    },
    # 日期类型
    'date': {
        'type': datetime,
        'str_name': 'datetime',
        'min_length': 0,
        'max_length': 65535
    },
    'time': {
        'type': datetime,
        'str_name': 'datetime',
        'min_length': 0,
        'max_length': 65535
    },
    'year': {
        'type': datetime,
        'str_name': 'datetime',
        'min_length': 0,
        'max_length': 65535
    },
    'datetime': {
        'type': datetime,
        'str_name': 'datetime',
        'min_length': 0,
        'max_length': 65535
    },
    'timestemp': {
        'type': datetime,
        'str_name': 'datetime',
        'min_length': 0,
        'max_length': 65535
    },
    # 浮点类型
    'float': {
        'type': float,
        'str_name': 'float',
        'min_length': 0,
        'max_length': sys.maxsize
    },
    'double': {
        'type': float,
        'str_name': 'float',
        'min_length': 0,
        'max_length': sys.maxsize
    },
    'tinyint': {
        'type': int,
        'str_name': 'int',
        'min_length': 0,
        'max_length': 1
    },
    'smallint': {
        'type': int,
        'str_name': 'int',
        'min_length': 0,
        'max_length': 2
    },
    'mediumint': {
        'type': int,
        'str_name': 'int',
        'min_length': 0,
        'max_length': 3
    },
    # 整数类型
    'int': {
        'type': int,
        'str_name': 'int',
        'min_length': 0,
        'max_length': 4
    },
    'bigint': {
        'type': int,
        'str_name': 'int',
        'min_length': 0,
        'max_length': 8
    }
}


# 计算数字字节数
def count_int_bytes(num: int):
    '''
    计算整形所占内存字节数
    :param num:
    :return:
    '''
    byte_num = int(len(re.sub('0b', '', bin(num))) / 8) + 1
    return byte_num


def count_str_bytes(string: str):
    '''
    计算字符串所占内存字节数
    :param string:
    :return:
    '''
    # byte_num = int(len(re.sub('0b', '', bin(int(string.encode().hex(), 16))))) + 1
    byte_num = len(string)
    return byte_num


def count_float_bytes(float_num: float):
    '''
    暂时弃用
    :param float_num:
    :return:
    '''
    byte_num = int(len(re.sub('0b', '', bin(int(hex(struct.pack("<f", float_num)), 16))))) + 1
    return byte_num


def check_data(data, type_str: str):
    '''
    检查数据是否合法
    :param data: 数据
    :param type_str: 类型字符串
    :return:
    '''
    for key in db_type_python_dict.keys():
        if key == re.sub('\(.*\)', '', type_str):
            data_struct_info = db_type_python_dict[key]
            max_length = data_struct_info['max_length']
            min_length = data_struct_info['min_length']
            length_info = re.sub('\(|\)', '', re.sub(key, '', type_str))
            if len(length_info) > 0:
                try:
                    max_length = int(length_info)
                except Exception as e:
                    sys.stderr.write(e)
                    sys.stderr.flush()
            try:
                data_bytes = None

                if data_struct_info['type'] is int and isinstance(data, int):
                    data_bytes = count_int_bytes(data)
                elif data_struct_info['type'] is str and isinstance(data, str):
                    data_bytes = count_str_bytes(data)
                elif data_struct_info['type'] is datetime and isinstance(data, datetime):
                    data_bytes = count_str_bytes(data.strftime('yyyy-MM-dd HH:mm:ss'))

                if data_bytes and data_bytes > min_length - 1 and data_bytes < max_length + 1:
                    return True
                else:
                    return False
            except:
                raise Exception(
                    '数据类型错误( data_type = ' +
                    str(type(data)) +
                    ' , db_type = ' +
                    type_str +
                    ' , required_type = ' +
                    str(data_struct_info['type']) + ' ) '
                )

    raise Exception(
        '不支持的数据类型( data = ' +
        (type(data)) +
        ' ) '
    )


def set_check(data_type):
    def fun(f):
        def arg(*args, **kwargs):
            value = args[1] if len(args) > 1 else kwargs['value']
            if check_data(value, data_type):
                result = f(*args, **kwargs)
                return result
            else:
                raise Exception(
                    '数据类型校验不通过( data = ' +
                    value +
                    ' , data_type = ' +
                    str(type(value)) +
                    ' , db_type = ' +
                    data_type +
                    ' )'
                )

        return arg

    return fun
