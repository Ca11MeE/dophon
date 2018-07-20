from dophon.mysql import Pool, Connection
from dophon import mysql
from dophon import logger
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
pool = Pool.Pool().initPool(5, Connection.Connection)

logger.inject_logger(globals())

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

    def before_select(self, fields_list: list, has_where: bool) -> str:
        result = 'SELECT ' + \
                 getattr(self, 'fields')(fields_list) + \
                 ' FROM ' + \
                 getattr(self, 'table_map_key') + \
                 (
                     (' AS ' + getattr(self, '__alias'))
                     if getattr(self,'__alias') != getattr(self,'table_map_key') else ''
                 ) + \
                 (getattr(self, 'where')() if has_where else '')
        return result

    def select(self, fields: list = [], has_where: bool = True) -> list:
        """
        查询并获取该表结果集
        :param fields: 列参
        :return: <list> 多条结果列表
        """
        sql = self.before_select(fields, has_where)
        logger.info('执行:', sql)
        result = []
        cursor = pool.getConn().getConnect().cursor()
        cursor.execute(sql)
        if not sql.startswith('select') and not sql.startswith('SELECT'):
            data = [[cursor.rowcount]]
            description = [['row_count']]
        else:
            data = cursor.fetchall()
            description = cursor.description
        result = mysql.sort_result(data, description, result)
        return result

    def select_one(self, fields: list = []) -> dict:
        """
        查询一条结果集
        :param fields: 列参
        :return: <dict> 单条结果集字典
        """
        if hasattr(self, '__field_callable_list') and len(getattr(self, '__field_callable_list')) > 0:
            # 存在可生成的查询条件
            result = self.select(fields=fields)
            if len(result) == 1:
                return result
            else:
                logger.error('过多结果集')
                raise Exception('过多结果集')
        else:
            logger.error('无法预料的唯一结果集,找不到查询过滤条件')
            raise Exception('无法预料的唯一结果集,找不到查询过滤条件')

    def select_all(self, fields: list = []) -> list:
        """
        同select
        :param fields:
        :return:
        """
        if hasattr(self, '__field_callable_list') and len(getattr(self, '__field_callable_list')) > 0:
            logger.error('警告:存在查询过滤条件\n')
        return self.select(fields=fields, has_where=False)
