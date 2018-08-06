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


class Selelct:
    """
    查询结构类
    """

    def before_select(self, fields_list: list, has_where: bool) -> str:
        result = 'SELECT ' + \
                 getattr(self, 'fields')(fields_list) + \
                 ' FROM ' + \
                 (

                     getattr(self, 'table_map_key') + \
                     (
                         (' AS ' + getattr(self, '__alias'))
                         if getattr(self, '__alias') != getattr(self, 'table_map_key') else ''
                     )
                     if not getattr(self, '__join_list') else (getattr(self, 'exe_join')())) \
                 + \
                 (getattr(self, 'where')() if has_where else '')
        print(result)
        return result

    def select(self, fields: list = [], has_where: bool = True) -> list:
        """
        查询并获取该表结果集
        :param fields: 列参
        :return: <list> 多条结果列表
        """
        sql = self.before_select(fields, has_where)
        logger.info('执行: %s', sql)
        result = []
        connection = pool.getConn().getConnect()
        cursor = connection.cursor()
        cursor.execute(sql)
        if not sql.startswith('select') and not sql.startswith('SELECT'):
            data = [[cursor.rowcount]]
            description = [['row_count']]
        else:
            data = cursor.fetchall()
            description = cursor.description
        connection.commit()
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
            elif len(result) > 1:
                logger.error('过多结果集')
                raise Exception('过多结果集')
            else:
                return None
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
            logger.warning('警告:存在查询过滤条件')
        return self.select(fields=fields, has_where=False)


class Insert:
    """
    新增结构类
    """

    def before_insert(self):
        result = 'INSERT INTO ' + \
                 getattr(self, 'table_map_key') + ' ' + \
                 getattr(self, 'values')()
        # print(result)
        return result

    def insert(self) -> int:
        """
        新增结果集
        :return: <int> 影响行数
                [{'row_count': '0'}]
        """
        sql = self.before_insert()
        logger.info('执行: %s', sql)
        result = []
        connection = pool.getConn().getConnect()
        cursor = connection.cursor()
        cursor.execute(sql)
        if not sql.startswith('select') and not sql.startswith('SELECT'):
            data = [[cursor.rowcount]]
            description = [['row_count']]
        else:
            data = cursor.fetchall()
            description = cursor.description
        connection.commit()
        result = mysql.sort_result(data, description, result)[0]['row_count']
        return int(result)


class Update():
    """
    更新结构类
    """

    def before_update(self, update: list, where: list):
        result = 'UPDATE ' + getattr(self, 'table_map_key') + \
                 getattr(self, 'set')(update) + \
                 getattr(self, 'where')(where)
        # print(result)
        return result

    def update(self, update: list = [], where: list = []) -> int:
        """
        更新结果集
        :param update: 更新列参
        :param where: 条件列参
        :return: <int> 影响行数
        """
        sql = self.before_update(update, where)
        logger.info('执行: %s', sql)
        result = []
        connection = pool.getConn().getConnect()
        cursor = connection.cursor()
        cursor.execute(sql)
        if not sql.startswith('select') and not sql.startswith('SELECT'):
            data = [[cursor.rowcount]]
            description = [['row_count']]
        else:
            data = cursor.fetchall()
            description = cursor.description
        connection.commit()
        result = mysql.sort_result(data, description, result)[0]['row_count']
        return int(result)


class Delete():
    """
    删除结构类
    """

    def before_delete(self, where: list):
        result = 'DELETE FROM ' + getattr(self, 'table_map_key') + ' ' + getattr(self, 'where')(where)
        # print(result)
        return result

    def delete(self, where: list = []) -> int:
        """
        删除结果集

        :param where: 条件列参
        :return: <int> 影响行数
        """
        sql = self.before_delete(where)
        logger.info('执行: %s', sql)
        result = []
        connection = pool.getConn().getConnect()
        cursor = connection.cursor()
        cursor.execute(sql)
        if not sql.startswith('select') and not sql.startswith('SELECT'):
            data = [[cursor.rowcount]]
            description = [['row_count']]
        else:
            data = cursor.fetchall()
            description = cursor.description
        connection.commit()
        result = mysql.sort_result(data, description, result)[0]['row_count']
        return int(result)


class Struct(Selelct, Insert, Update, Delete):
    """
    查询语句结构类
    """
