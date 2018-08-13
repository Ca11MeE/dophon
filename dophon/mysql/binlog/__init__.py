# coding: utf-8
from dophon.mysql.binlog import ZipBinLog
from dophon import logger

"""
xml文件增强功能封装单元
author:CallMeE
date:2018-06-01
"""

logger.inject_logger(globals())

class BinCache():
    _bin = ''
    _file = ''
    _false_fun = None

    def __init__(self, file):
        # 初始化原始bin对象
        self._bin = ZipBinLog.zip_as_bin(file)
        self._file = file

    def set_false_fun(self, fun):
        self._false_fun = fun

    def chk_diff(self):
        if self._bin == ZipBinLog.zip_as_bin(self._file):
            pass
        else:
            logger.info('文件发生增量更新(' + self._file + ')')
            # 执行增量更新方法
            if not self._false_fun:
                pass
            else:
                self._false_fun()
        # 重新初始化对象binlog信息
        self._bin = ZipBinLog.zip_as_bin(self._file)


def def_false_fun(file):
    logger.info('xml文件发生增量改变!(' + str(file) + ')')
