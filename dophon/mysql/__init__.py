# coding: utf-8
import dophon.reader as reader
from dophon.mysql import Pool, Connection, PageHelper
from dophon.mysql.remote.Cell import Cell
import threading
import re
from dophon.mysql import binlog
from dophon.mysql.binlog import Schued
from dophon import properties
from dophon import logger

"""
后续开发;
(完成)1.远程读取mapperxml
(完成)2.语句对象定时更新暂定为本地xml文件增量binlog更新,后续开发远程增量更新(流程未定)
    (完成)2.1本地binlog处理对比
    (完成)2.2远程binlog处理对比
(半完成)3.binlog生成算法以及对比算法以及增量写入
(完成)4.细粒度事务控制
(完成)5.配置文件配置连接数
(完成)6.参照mybatis完成sql骨架拼写


单条语句执行demo:
# obj = getDbObj(project_path + '/mappers/ShopGoodsMapper.xml')
# setObjUpdateRound(obj, '2')
# obj.exe_sql("findGoodsList")

批量语句执行DEMO:
# obj=getDbObj(path=project_path +'/mysql/test.xml',debug=True)
# obj.exe_sql_obj_queue(queue_obj={"test":(1,2),"test":(2,3)})
或者
# obj.exe_sql_queue(method_queue=['test','test','test_s','test','test'],args_queue=[('1','2'),('2','3'),(),('3','4'),('3','4')])
"""

# 定义连接池实例
pool = None

# 定义项目路径
project_path = properties.project_root

logger.inject_logger(globals())

obj_manager = {}


class BlockingThreadError(Exception):
    pass


class curObj:
    _page = False
    _db = None
    _cursor = None
    _conn = None
    _debug = False
    _cursor = None
    sql = None
    lock = threading.Lock()

    def __init__(self, db, path: str, poolFlag: bool, debug: bool):
        """
        初始化结果集对象
        :param db: 连接工具实例(连接池或单个连接)
        :param path: 结果集管理xml路径
        :param poolFlag: 连接池标识
        :param debug: 调试标识
        """
        self._debug = debug
        self._poolFlag = poolFlag
        self.sql = reader.Mapper()
        if poolFlag:
            # 连接池实例化
            self._pool = db
        else:
            self._db = db
        self.sql.openDom(path)
        self._path = path
        self._file_part_mark = re.sub('\\..*', '', path.split('/')[len(path.split('/')) - 1])
        self._sqls = self.sql.getTree()[self._file_part_mark]

    def refreash_sqls(self):
        """
        刷新sql语句(动态调试sql)
        ps:慎用
        :return:
        """
        global sql
        self.sql.openDom(self._path)
        self._sqls = self.sql.getTree()[self._file_part_mark]

    def check_conn(self):
        """
        检查数据库连接
        :return:
        """
        try:
            if not self._db:
                # 无连接,需要获取连接
                if self._poolFlag:
                    # 连接池
                    self._conn = self._pool.getConn()
                    self._db = self._conn.getConnect()
                else:
                    # 单个连接理论上只执行一次,过后直接关闭
                    self._db = Connection()
        except Exception as e:
            logger.error(e)
            raise Exception('检查连接失败')

    def set_cursor(self):
        """
        # 初始化指针(如果不存在指针)

        :return:
        """
        if not self._cursor:
            self._cursor = self._db.cursor()

    def get_sql(self, methodName: str, pageInfo, args=()):
        """
        # 获取sql语句(包含处理)

        :param methodName: 结果集代号
        :param pageInfo: 分页标识
        :param args: 结果集映射语句参数集
        :return:
        """
        # 单独连接实例化
        # 判断是否存在子节点
        if methodName not in self._sqls:
            logger.error('没有该方法!method: ' + str(methodName))
            raise Exception('没有该方法!method:' + str(methodName))
        _sql = self._sqls[methodName]
        # 判断是否分页(总开关)
        # 开启之后该实例所有语句都认为是 需要分页
        # 慎用!!!!
        if self._page:
            # 分页
            _sql = _sql + 'limit ' + str((self._pageNum - 1) * self._pageSize) + ',' + str(self._pageSize)
        if pageInfo:
            # 分页
            _sql = _sql + PageHelper.depkg_page_info(pageInfo)
        # 判断是否骨架拼接
        if args:
            # 检查骨架实参传入类型,并作不同处理
            if type(args) is type(()):
                if re.match(r'(\#|\$)\{.*\}', _sql):
                    logger.error('骨架与参数不匹配')
                    raise Exception('骨架与参数不匹配')
                _sql = _sql % args[:]
            elif type(args) is type({}):
                for key in args.keys():
                    reg_str = r'(\#|\$)\{' + str(key) + '\}'
                    if not re.search(reg_str, _sql):
                        '''
                        此处有几种情况:
                        1.语句骨架不存在该key的空位(多余参数)
                        2.骨架参数与骨架不对应(多余空位)
                        '''
                        pass
                    else:
                        _sql = re.sub('\#\{' + str(key) + '\}', '\'' + str(args[key]) + '\'',
                                      re.sub('\$\{' + str(key) + '\}', str(args[key]), _sql))
                # 多余空位检查
                if re.search('(\#|\$)\{' + str(key) + '\}', _sql):
                    logger.error('存在无法配对的骨架参数')
                    raise Exception('存在无法配对的骨架参数')
            else:
                try:
                    _sql = _sql % args[:]
                except Exception as e:
                    logger.error(e + '\n')
                    raise e
        # 去除注释与空格,换行等
        __sql = re.sub('\\s+', ' ', re.sub('<!--.*-->', ' ', _sql))
        return __sql

    def set_page(self, pageNum: str, pageSize: str):
        """
        # 设定分页信息

        :param pageNum:页号(从0开始)
        :param pageSize: 页容(>0)
        :return:
        """
        self._pageNum = pageNum
        self._pageSize = pageSize
        self._page = True

    def initial_page(self):
        """
        重置结果集实例的分页信息
        :return:
        """
        self._page = False

    def exe_sql_obj_queue(self, queue_obj={}) -> dict:
        # 批量执行语句(整体版)
        """
        queue_obj中key为方法名,value为参数
        注意!!!!
        对于一个业务来说,一个sql方法只使用一次(因为有内部数据缓存)
        若其中有重复方法,建议用分割版
        """

        if queue_obj:
            methods = list(queue_obj.keys())
            args = list(queue_obj.values())
            return self.exe_sql_queue(method_queue=methods, args_queue=args)
        else:
            logger.error('queue_obj参数不正确')
            raise Exception('queue_obj参数不正确')

    def exe_sql_queue(self, method_queue=[], args_queue=[]) -> dict:
        # 批量执行语句(拆分版)
        """
        method_queue中存放顺序执行的sql方法名[str]
        args_queue中存放对应下标方法的参数元组[()]
        若其中包含select无条件参数语句,请用空元组()占位
        """
        self.lock.acquire(blocking=True)
        result = {}
        # 参数检查
        if not method_queue:
            logger.error('语句方法为空')
            raise Exception('语句方法为空')
            return
        if not args_queue:
            logger.error('语句参数列表为空')
            raise Exception('语句参数列表为空')
            return
        self.check_conn()
        self.set_cursor()
        try:
            # 开启事务
            # 批量取语句(以方法名为准,多于参数队列元素将丢弃)
            while method_queue:
                method = method_queue.pop(0)
                args = args_queue.pop(0)
                """
                对于增改查来说,并不需要分页,参数列表是必须的
                """
                _sql = self.get_sql(methodName=method, args=args, pageInfo=None)
                # 执行sql语句
                self._cursor.execute(_sql)
                '''
                尝试执行语句成功后会解析结果集
                '''
                if re.match('^\\s*(s|S)(e|E)(l|L)(e|E)(c|C)(t|T)\\s+.+', _sql):
                    data = self._cursor.fetchall()
                    description = self._cursor.description
                else:
                    data = [[self._cursor.rowcount]]
                    description = [['row_count']]
                current_result = sort_result(data, description, result)
                # 调试模式打印语句
                if self._debug:
                    print_debug(methodName=method, args=args, sql=_sql, result=self._cursor.rowcount)
                    # 事务提交(pymysql要求除查询外所有语句必须手动提交)
                if method in result:
                    result[method + str(len(result))] =current_result
                else:
                    result[method]=current_result
        except Exception as e:
            logger.error(str(e) + '\n')
            self._db.rollback()
            logger.error('事务回滚' + str(method_queue))
            raise e
        else:
            self._db.commit()
            logger.info('事务提交' + str(method_queue))
        finally:
            self.lock.release()
            # 关闭连接
            self.close()
            return result

    def exe_sql(self, methodName='', pageInfo=None, args=()) -> list:
        """
        # 执行单条语句,返回结果列表(select more)

        # 防报错参数设定默认值
        :param methodName: 结果集映射代号
        :param pageInfo: 结果集分页信息
        :param args: 结果集查询参数
        :return: <select>  ==>  查询结果
                  <insert,update,delete>  ==>  有效行数
        """
        self.lock.acquire(blocking=True)
        # 参数检查
        if not re.sub('\s+', '', methodName):
            logger.error('语句方法为空')
            raise Exception('语句方法为空')
            return
        self.check_conn()
        self.set_cursor()
        # 定义返回结果集
        result = []
        try:
            if pageInfo and type(pageInfo) is type({}):
                _sql = self.get_sql(methodName=methodName, pageInfo=pageInfo, args=args)
            else:
                _sql = self.get_sql(methodName=methodName, args=args, pageInfo=None)
        except Exception as ex:
            logger.error(ex)
            return result
        try:
            # 试执行语句
            self._cursor.execute(_sql)
            self._db.commit()
            self.initial_page()
            '''
            尝试执行语句成功后会解析结果集
            '''
            if re.match('^\\s*(s|S)(e|E)(l|L)(e|E)(c|C)(t|T)\\s+.+', _sql):
                data = self._cursor.fetchall()
                description = self._cursor.description
            else:
                data = [[self._cursor.rowcount]]
                description = [['row_count']]
            result = sort_result(data, description, result)
        except Exception as e:
            self._db.rollback()
            self.initial_page()
            logger.error("执行出错,错误信息为:" + str(e) + 'sql语句为:' + _sql)
        finally:
            # 关闭连接
            self.close()
            # 调试模式语句执行信息打印
            if self._debug:
                print_debug(methodName=methodName, args=args, sql=_sql, result=result)
            self.lock.release()
        # 非查询语句返回影响行数
        if result:
            if re.match('^\\s*(s|S)(e|E)(l|L)(e|E)(c|C)(t|T)\\s+.+', _sql):
                return result
            else:
                return data[0][0]
        else:
            return []

    def exe_sql_single(self, methodName='', pageInfo=None, args=()) -> object:
        """
        返回单个对象(select one)
        # 防报错参数设定默认值
        :param methodName: 结果集映射代号
        :param pageInfo: 结果集分页信息
        :param args: 结果集查询参数
        :return: <select>  ==>  查询结果
                  <insert,update,delete>  ==>  有效行数
        """
        result = self.exe_sql(methodName=methodName, pageInfo=pageInfo, args=args)
        if isinstance(result, list):
            # 列表类型执行取值
            if 1 < len(result):
                # 多个结果
                logger.error('过多结果')
                raise Exception('过多结果')
            elif 0 == len(result):
                return None
            else:
                return result[0]
        else:
            return result

    def close(self):
        """
        (单个连接):关闭数据库连接
        (连接池):归还连接
        :return:
        """
        self._cursor.close()
        if self._poolFlag:
            # 为连接池定义
            pool.closeConn(self._conn)
            # 归还连接后清除指针
            self._cursor = None
            self._db = None
            self._conn = None
        else:
            # 为单独连接定义
            self._db.close()

    def insert_to_update_dispacther(self, millionSecond):
        """
        # 定义插入更新调度方法

        :param millionSecond: 更新频率
        :return:
        """
        if isinstance(millionSecond, int):
            w_time = millionSecond
            pass
        else:
            try:
                w_time = int(millionSecond)
            except Exception as e:
                logger.error(e)

        # 此处为增量更新代码
        '''
        临时思路
        1.设定定时间隔
        2.传入当前语句对象
        3.内部压缩保存binlog
        4.定时完毕重新获取语句,获取新语句对象binlog
        5.对比binlog
            5.1若更新后binog无差异则不作处理
            5.2若存在差异,替换语句对象
        '''
        self._bin_cache = binlog.BinCache(self._path)
        # 添加变更处理
        self._bin_cache.set_false_fun(self.refreash_sqls)
        # 调度器添加任务
        Schued.sech_obj(fun=self._bin_cache.chk_diff, delay=w_time).enter()

    """
    细粒度sql语句执行组
    """

    def execute(self, method_name: str, pageInfo=None, args=()):
        if self.lock.locked():
            raise BlockingThreadError('还有事务尚未提交!!!')
        self.lock.acquire(blocking=True)
        self._cursor.execute(sql)

    def commit(self):
        self._db.commit()
        self.lock.release()

    def rollback(self):
        self._db.rollback()
        self.lock.release()


def sort_result(data: list, description: tuple, result: list) -> list:
    """
    # 整理结果集并返回
    :param data: 数据集
    :param description:数据描述
    :param result: 结果列表(或许产生多个集合)
    :return:
    """
    for index in range(len(data)):
        item = data[index]
        r_item = {}
        for i in range(len(item)):
            colName = description[i][0]
            val = item[i]
            value = 'none'
            if type(val) is not type(None):
                value = str(val)
            # 组装data
            r_item[colName] = value
        # 组装结果集
        result.append(r_item)
    return result


def getDbObj(path, debug: bool = False, auto_fix: bool = False):
    """
    获取数据表实例
    :param path: xml文件路径
    :param debug: 是否开启调试模式
    :param auto_fix: 是否开启路径修复模式(损耗资源) <===  待测试
    :return: xml对应实例
    """
    if pool is None:
        logger.error('连接池未定义')
        raise Exception('连接池未定义')
    if 0 >= pool.size():
        # 配置属性生命周期过短,拟用__import__导入减轻内存废址
        prop = __import__('properties')
        if hasattr(prop, 'pool_conn_num'):
            pool.initPool(getattr(prop, 'pool_conn_num'), Connection.Connection)
        else:
            # 初始5个连接
            pool.initPool(5, Connection.Connection)
    if isinstance(path,str):
        if auto_fix:
            pattern = re.sub(r'\\', r'\\\\', re.sub('/', '\\/', project_path))
            if not re.search(pattern, path):
                r_path = str(project_path) + str(path)
            else:
                r_path = str(path)
        else:
            r_path = path
    elif isinstance(path,Cell):
        r_path = path.getPath()
    else:
        raise TypeError('结果集路径类型错误')
    # 数据语句对象改为单例模式获取
    if r_path in obj_manager:
        return obj_manager[r_path]
    singleton_obj = curObj(pool, r_path, True, debug)
    obj_manager[r_path] = singleton_obj
    return singleton_obj


def setObjUpdateRound(obj: curObj, second: int):
    """
    设置结果集映射实例定时更新
    :param obj: 结果集映射实例
    :param second: 更新频率
    :return:
    """
    if isinstance(obj, curObj):
        obj.insert_to_update_dispacther(second)
    else:
        logger.error('类型错误!!!!')
        raise Exception('类型错误!!!!')


def print_debug(methodName: str, sql: str, args: dict, result: list):
    """
    # 调试模式下的语句信息打印

    :param methodName: 结果集映射实例的结果集代号
    :param sql: 结果集生成语句
    :param args: 结果集实例执行参数
    :param result: 结果集实例执行结果
    :return:
    """
    print('METHOD:==>' + methodName)
    print('SQL:=====>' + sql)
    print('PARAMS:==>' + str(args))
    if isinstance(result, list):
        if result and result[0]:
            # 拿出列名
            print('ROWS:====>' + str(list(result[0].keys())))
            print('RESULT:==>' + str(list(result[0].values())))
            for r in result[1:]:
                print('=========>' + str(list(r.values())))
        else:
            print('ROWS:====>None')
            print('RESULT:==>None')
    if isinstance(result, int):
        print('ROWS:====>', result)


def whereCause(args: dict) -> str:
    """
    将字典转换为sql条件语句
    :param args: 字典(条件字典)
    :return: sql条件语句
    """
    cache = []
    for key in args.keys():
        cache.append(str(key) + '=' + str(args[key]))
    return 'WHERE ' + re.sub('\[|\]|\\\"|\\\'', '', re.sub(',', ' AND ', str(cache)))


db_obj = getDbObj
update_round = setObjUpdateRound
where = whereCause

__all__ = [
    'db_obj', 'update_round', 'where'
]
