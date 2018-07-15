from dophon.mysql import Connection
from dophon import mysql
import types
import re
from dophon.orm.db_obj.type_dict import db_type_python_dict
from dophon.orm.db_obj.type_dict import set_check
from dophon.orm.db_obj.function_class import *
from  dophon.orm.query_structor import Struct

# 初始化表结构缓存
table_cache = {}


def create_class(table_name: str, table_args: list):
    """
    创建数据表类
    :param table_name:  表名
    :param table_args: 表参数
    :return:
    """
    class_obj = type(table_name, (WhereAble, ValueAble,Struct), {'__alias': table_name, 'table_map_key': table_name})
    for table_arg in table_args:
        # 获取表字段名以及属性
        table_arg_field = table_arg['Field']
        table_arg_type = table_arg['Type']
        table_arg_null = table_arg['Null']
        table_arg_key = table_arg['Key']
        table_arg_default = table_arg['Default']

        '''
        映射类属性方法组装
        '''
        setter_code = compile(
            'def setter_' + table_arg_field + '(self,value):' +
            '\n\tself._' + table_arg_field + ' = value' +
            '\n\tself.append(\'' + table_arg_field + '\')',
            '',
            'exec'
        )
        setter_function_code = [c for c in setter_code.co_consts if isinstance(c, types.CodeType)][0]
        setter_method = set_check(table_arg_type)(types.FunctionType(setter_function_code, {}))

        getter_code = compile(
            'def getter_' + table_arg_field + '(self):' +
            '\n\treturn self._' + table_arg_field,
            '',
            'exec'
        )
        getter_function_code = [c for c in getter_code.co_consts if isinstance(c, types.CodeType)][0]
        getter_method = types.FunctionType(getter_function_code, {})

        setattr(
            class_obj,
            '_' + table_arg_field,
            table_arg_default if table_arg_null == 'YES' else None,
        )

        setattr(
            class_obj,
            table_arg_field,
            property(getter_method, setter_method)
        )

    '''
    映射类固定方法组装
    '''
    # 重载直接调用运算符
    callable_code = compile(
        'def __call__(self,call_list):' +
        '\n\treturn self.get_fields(call_list)',
        '',
        'exec'
    )
    callable_function_code = [c for c in callable_code.co_consts if isinstance(c, types.CodeType)][0]
    callable_method = types.FunctionType(callable_function_code, {})

    setattr(
        class_obj,
        '__call__',
        callable_method
    )

    # 重载映射类别名运算符
    alias_code = compile(
        'def alias(self,alias_name:str):' +
        '\n\tself.__alias=alias_name' +
        '\n\treturn self',
        '',
        'exec'
    )
    alias_function_code = [c for c in alias_code.co_consts if isinstance(c, types.CodeType)][0]
    alias_method = types.FunctionType(alias_function_code, {})

    setattr(
        class_obj,
        'alias',
        alias_method
    )

    return class_obj


class OrmManager:
    def add_orm_obj(self, table_obj: object):
        if 'table_name' in table_obj:
            # 添加表名单位
            table_name = table_obj['table_name']
            # 编译表名属性方法(property)
            getter_module_code = compile(
                'def ' + table_name + '(self):\n\treturn self._' + table_name,
                '',
                'exec'
            )
            function_code = [c for c in getter_module_code.co_consts if isinstance(c, types.CodeType)][0]
            getter_method = types.FunctionType(function_code, {})
            # 获取表结构
            table_arg = table_obj['table_obj']
            if not search_class_by_name(table_name):
                # 组装新类
                table_class = create_class(table_name, table_arg)
                save_cache(table_name,table_class)
            else:
                table_class=get_cache(table_name)
            # 植入类内
            setattr(OrmManager, '_' + table_name, table_class)
            setattr(OrmManager, table_name, property(getter_method))
        else:
            raise Exception('插入对象异常')


def init_tables_in_db(manager: OrmManager, tables: list = []):
    print('数据库全表ORM初始化开始' if not tables else str(tables[:]) + 'ORM初始化开始')
    connect = Connection.Connection().getConnect()
    cursor = connect.cursor()
    cursor.execute('SHOW TABLES')
    connect.commit()
    # 整理数据表名列表
    for tup_item in cursor.fetchall():
        if tables:
            if tup_item[0] in tables:
                init_table_param(tup_item[0], manager)
        else:
            init_table_param(tup_item[0], manager)
    connect.close()
    print('数据库ORM初始化完毕')


def init_table_param(table_name, manager: OrmManager):
    connect = Connection.Connection().getConnect()
    cursor = connect.cursor()
    cursor.execute('DESC ' + table_name)
    connect.commit()
    titles = cursor.description
    values = cursor.fetchall()
    result = mysql.sort_result(values, titles, [])
    table_obj = {
        'table_name': table_name,
        'table_obj': result
    }
    manager.add_orm_obj(table_obj)
    connect.close()


def save_cache(table_name: str, table_class: object):
    """
    将orm映射类写入缓存
    :param table_class: orm映射类
    :return:
    """
    print('保存映射缓存:',table_name,str(table_class))
    table_cache[table_name] = table_class

def get_cache(table_name:str) -> object:
    """
    根据表名获取orm映射类缓存
    :param table_name: 映射表名
    :return: orm映射类
    """
    print('获取映射缓存:',table_name)
    return table_cache[table_name]

def search_class_by_name(table_name:str) -> bool:
    """
    根据表名查找缓存
    :param table_name: 映射表名
    :return: 是否命中缓存
    """
    print('检查映射缓存:',table_name)
    return table_name in table_cache