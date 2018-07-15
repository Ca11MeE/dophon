import re

"""
功能特性类集合
"""

__all__ = ['WhereAble', 'ValueAble', 'SetAble', 'OrmObj']


class OrmObj(object):
    """
    表映射基础类(标注作用)
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
            self.__field_callable_list = []

    def append(self, field_name: str):
        """
        内部方法:记录字段名
        :param field_name:
        :return:
        """
        self.__field_callable_list.append(field_name)

    def get_fields(self, list: list = []) -> dict:
        """
        获取字段映射
        :param list:
        :return:
        """
        cache = {}
        for f_name in self.__field_callable_list if not list else list:
            if hasattr(self, f_name):
                cache[f_name] = getattr(self, f_name)
            else:
                print('警告:表(', getattr(self, 'table_map_key'), ')缺失字段(', f_name, '),表映射存在风险')
        return cache

    def get_field_list(self, list: list = []) -> list:
        """
        获取字段列表
        :param list:
        :return:
        """
        cache = []
        for f_name in self.__field_callable_list if not list else list:
            if getattr(self, f_name):
                cache.append(getattr(self, '__alias') + '.' + f_name)
            else:
                print('警告:表(', getattr(self, 'table_map_key'), ')缺失字段(', f_name, '),表映射存在风险')
        return cache

    def fields(self):
        fields_list = self.get_field_list()
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
            cache.append(str(key) + '=' + (str(
                args[key]) if isinstance(args[key], int) or isinstance(args[key], float) else (
                '{' + str(args[key]) + '}')))
        return re.sub('\{|\}', '\'', re.sub('\[|\]|\\\"|\\\'', '', re.sub(',', ' AND ', str(cache))))

    def where(self, fields: list = []) -> str:
        """
        获取条件执行语句
        :param fields:条件列表
        :return:
        """
        if fields:
            args = self.get_fields(fields)
        else:
            return ''
        return ' WHERE ' + self.where_cause(args)


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
        return ' SET ' + self.where_cause(args)


class JoinAble(OrmObj):
    """
    可关联化功能类
    """

    def __init__(self):
        """
        初始化关联列表
        """
        self.__join_list = []

    def left_join(self, target: FieldsCallable):
        """
        左关联功能
        :param target: 关联实例
        :return: 自身实例
        """
        self.__join_list.append(target)
        return self

    def right_join(self, target):
        """
        右关联功能
        :param target: 关联实例
        :return: 自身实例
        """
        if isinstance(target, JoinAble):
            target.left_join(self)
            return self
        else:
            raise Exception('关联对象不支持!!!')

    def union(self):
        pass
