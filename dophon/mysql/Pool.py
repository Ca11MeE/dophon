# coding: utf-8
#  连接
from dophon.mysql import Connection
from dophon import logger
import threading
"""
连接池
author:CallMeE
date:2018-06-01
"""

logger.inject_logger(globals())


class Pool():
    _size = 0

    # 初始化连接池
    def initPool(self, num:int, Conn:Connection):
        _pool = []
        self._Conn = Conn
        for item_c in range(num):
            # 遍历定义连接放入连接池
            conn = Conn()
            _pool.append(conn)
        self._pool = _pool
        self._size = num
        return self

    def __init__(self):
        logger.info('初始化连接池')

    # 定义取出连接
    def getConn(self) -> Connection:
        __pool = self._pool
        if __pool:
            lock = threading.Lock()
            lock.acquire(blocking=True)
            currConn = __pool.pop(0)
            if currConn.testConn():
                # 连接有效
                # 不作处理
                pass
            else:
                logger.info('连接无效')
                currConn.reConn()
            lock.release()
            return currConn
        else:
            # 连接数不足则新增连接
            conn = Connection.Connection()
            self._pool.append(conn)
            return self.getConn()

    # 定义归还连接
    def closeConn(self, conn):
        self._pool.append(conn)

    # 定义查询连接池连接数
    def size(self):
        return self._size

    # 定义释放所有连接
    def free_pool(self):
        for conn in self._pool:
            conn.getConnect().close()