from dophon.orm.db_obj.function_class import *

"""
查询语句结构映射

结构:
select
<Field>
from
<tables>
where
<param_dicts>
<sort_param>
"""


class Fields:
    """
    查询语句查询列参数类
    """

    def __init__(self, *args, **kwargs):
        print(*args)
        print(**kwargs)


class Struct():
    """
    查询语句结构类
    """

    def before_select(self, orm_obj: OrmObj, fields: list) -> str:
        result='SELECT ' + orm_obj.fields() + ' FROM ' + orm_obj.table_map_key + orm_obj.where(fields)
        return result

    def select(self, fields: list = []):
        sql = self.before_select(self, fields)
        print('执行:', sql)
