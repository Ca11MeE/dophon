import re
from dophon.orm.db_obj.function_class.func_tools import Parseable

"""
功能特性类集合
"""

__all__ = ['WhereAble', 'ValueAble', 'SetAble', 'OrmObj', 'JoinAble', 'Parseable']


class OrmObj(object):
    """
    表映射基础类(标注作用)

    待添加:sql关键字保护策略算法
    """
    pass


class FieldsCallable(OrmObj):
    """
    可取出内置数据集合的功能类
    """

    def __init__(self):
        """
        初始化类功能实现的数据域
        """
        if not hasattr(self, '__field_callable_list'):
            setattr(self, '__field_callable_list', [])
            self.__field_callable_list = []

    def append(self, field_name: str):
        """
        内部方法:记录字段名
        :param field_name:
        :return:
        """
        f_list = getattr(self, '__field_callable_list')
        f_list.append(field_name)
        setattr(self, '__field_callable_list', f_list)
        self.__field_callable_list.append(field_name)

    def get_fields(self, f_list: list = []) -> dict:
        """
        获取字段映射
        :param list:
        :return:
        """
        cache = {}
        if hasattr(self, '__field_callable_list') and len(getattr(self, '__field_callable_list')) > 0:
            fs_name = getattr(self, '__field_callable_list')
        elif self.__field_callable_list:
            fs_name = self.__field_callable_list
        elif hasattr(self, '__default_arg_list'):
            fs_name = getattr(self, '__default_arg_list')
        else:
            fs_name = f_list

        for f_name in fs_name:
            if hasattr(self, f_name):
                if f_list:
                    if f_name in f_list:
                        cache[f_name] = getattr(self, f_name)
                        continue
                else:
                    cache[f_name] = getattr(self, f_name)
            else:
                print('警告:表(', getattr(self, 'table_map_key'), ')缺失字段(', f_name, '),表映射存在风险')
        return cache

    def get_field_list(self, f_list: list = []) -> list:
        """
        获取字段列表
        :param list:
        :return:
        """
        cache_list = list(self.get_fields(f_list=f_list).keys())
        cache = []
        for f_name in cache_list:
            cache.append(
                getattr(self, '__alias') + '.' +
                f_name
            )

        return cache

    def fields(self, fields: list = []):
        fields_list = self.get_field_list(fields)
        cache = re.sub('\[|\]|\\\'|\\\"', '', str(fields_list))
        return cache


class ValueAble(FieldsCallable):
    """
    可赋值化功能类
    """

    def __init__(self):
        """
        初始化类功能实现的数据域
        """
        FieldsCallable.__init__(self)

    def value_cause(self, args: dict) -> list:
        """
        将字典键值分离
        :param args: 字典对象
        :return:
        """
        keys = re.sub('\\\'', '', re.sub('\[', '(', re.sub('\]', ')', str(list(args.keys())))))
        values = re.sub('\[', '(', re.sub('\]', ')', str(list(args.values()))))
        return [
            keys
            ,
            values
        ]

    def values(self, fields: list = []) -> str:
        """
        获取条件赋值语句
        :param fields: 键值列表
        :return:
        """
        result = self.value_cause(self(fields))
        return result[0] + ' VALUES ' + result[1]


class WhereAble(FieldsCallable):
    """
    可条件化功能类
    """

    def __init__(self):
        """
        初始化类功能实现的数据域
        """
        FieldsCallable.__init__(self)

    def where_cause(self, args: dict) -> str:
        """
        将字典转换为sql条件语句
        :param args: 字典(条件字典)
        :return: sql条件语句
        """
        cache = []
        for key in args.keys():
            self_table_alias = \
                (getattr(self, '__alias') + '.' if getattr(self, '__alias') != getattr(self, 'table_map_key') else '')
            cache.append(
                self_table_alias +
                str(key) +
                '=' +
                (str(
                    args[key]) if isinstance(args[key], int) or isinstance(args[key], float) else (
                        '{' + str(args[key]) + '}')))
        return re.sub('\{|\}', '\'', re.sub('\[|\]|\\\"|\\\'', '', re.sub(',', ' AND ', str(cache))))

    def where(self, fields: list = []) -> str:
        """
        获取条件执行语句
        :param fields:条件列表
        :return:
        """
        if len(fields) > 0 or (
                hasattr(self, '__field_callable_list') and len(getattr(self, '__field_callable_list')) > 0):
            args = getattr(self, 'get_fields')(fields)
        else:
            return ''
        return ' WHERE ' + getattr(self, 'where_cause')(args)


class SetAble(WhereAble):
    """
    可更新化条件类
    """

    def __init__(self):
        """
        初始化类功能实现的数据域
        """
        FieldsCallable.__init__(self)

    def set(self, fields: list = []) -> str:
        """
        获取更新执行语句
        :param fields: 更新参数列表
        :return:
        """
        args = self.get_fields(fields)
        return ' SET ' + re.sub('AND', ',', self.where_cause(args))


class JoinAble(OrmObj):
    """
    可关联化功能类
    """

    def __init__(self):
        """
        初始化关联列表
        """
        if not hasattr(self, '__join_list'):
            setattr(self, '__join_list', [])
            self.__join_list = []

    def left_join(self, target, on_left_field: list, on_right_field: list):
        """
        左关联功能
        :param target: 关联实例
        :return: 自身实例
        """
        if not on_left_field or not on_right_field or len(on_left_field) > len(on_right_field):
            raise Exception('关联参数异常')
        if isinstance(target, JoinAble):
            setattr(self, '__join_list', [])
            getattr(self, '__join_list').append({
                'target': target,
                'left_field': on_left_field,
                'right_field': on_right_field
            })
            return self
        else:
            raise Exception('关联对象不支持!!!')

    def right_join(self, target, on_left_field: list, on_right_field: list):
        """
        右关联功能
        :param target: 关联实例
        :return: 自身实例
        """
        if isinstance(target, JoinAble):
            target.left_join(self, on_left_field, on_right_field)
            return self
        else:
            raise Exception('关联对象不支持!!!')

    def union(self):
        pass

    def exe_join(self) -> str:
        self_table_alias = \
            getattr(self, '__alias') if getattr(self, '__alias') != getattr(self, 'table_map_key') else ''

        result = [
            getattr(self, 'table_map_key') +
            (' AS ' if getattr(self, '__alias') != getattr(self, 'table_map_key') else '')
            + self_table_alias
        ]
        for join_obj in getattr(self, '__join_list'):
            # 获取关联对象
            obj = join_obj['target']
            join_obj_table_alias = \
                getattr(obj, '__alias') if getattr(obj, '__alias') != getattr(obj, 'table_map_key') else ''
            result.append(getattr(obj, 'table_map_key') +
                          (' AS ' if getattr(obj, '__alias') != getattr(obj, 'table_map_key') else '')
                          + join_obj_table_alias)
            # 获取关联键
            left_field = join_obj['left_field']
            right_field = join_obj['right_field']
            # 以关联左键为准
            on_fields_pair_sep = ' AND '
            on_fields_pair = []
            for index in range(len(left_field)):
                l_field = left_field[index]
                on_fields_pair.append(
                    self_table_alias + '.' + l_field +
                    ' = '
                    + join_obj_table_alias + '.' + right_field[index])
        return ' LEFT JOIN '.join(result) + ' ON ' + on_fields_pair_sep.join(on_fields_pair)
