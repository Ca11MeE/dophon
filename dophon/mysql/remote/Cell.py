# coding: utf-8
from urllib import request
import uuid, os, dophon.mysql as mysql, time, stat
import dophon.mysql.binlog.Schued as schued
from dophon import logger

"""
远程xml映射实例模板
author:CallMeE
date:2018-06-01


# 开启远程xml需要导入以下模块
# import mysql.remote as remote

demo:
remote_cell = remote.getCell('ShopGoodsMapper.xml', remote_path='http://127.0.0.1:8400/member/export/xml/ShopGoodsMapper.xml')
obj1 = getDbObj(remote_cell.getPath(), debug=True)

注意！！！
read_only设置远程xml文件是否为只读，注意防止与自动增量更新冲突
"""


logger.inject_logger(globals())


class cell():
    def __init__(self, file_name='', remote_path='', read_only=False):
        self._file_name = file_name
        self._remote_path = remote_path
        self._uid = uuid.uuid5(uuid.NAMESPACE_DNS, file_name)
        # 创建临时文件夹(安全性考虑，采用多层目录)
        self._file_path = mysql.project_path + sort_path(self._uid)
        # 检查路径
        if os.path.exists(self._file_path):
            pass
        else:
            os.makedirs(self._file_path)
        while True:
            # 下载远程文件
            try:
                response = request.urlretrieve(url=remote_path, filename=self._file_path + '/' + self._file_name)
                logger.info('加载远程mapper：' + response[0])
                # 放置路径
                self._abs_path = response[0]
                if read_only:
                    self.lock_to_read()
                break
            except Exception as e:
                logger.error(e)
                logger.error('连接远程计算机失败,请检查连接,3秒后重试(' + str(id(self)) + ')')
                time.sleep(3)

    # 重新加载文件
    def reload_file(self):
        # 放开写入权限
        if self.is_only_read():
            self.unlock_to_read()
            response = request.urlretrieve(url=self._remote_path, filename=self._file_path + '/' + self._file_name)
            self.lock_to_read()
        else:
            response = request.urlretrieve(url=self._remote_path, filename=self._file_path + '/' + self._file_name)
        logger.info('加载远程mapper：' + response[0])
        # 放置路径
        self._abs_path = response[0]
        # 链式调用（非必需）
        return self

    # 进入调度定时更新文件
    def reload_file_round(self, minute):
        schued.sech_obj(self.reload_file, minute * 60).enter()
        # 链式调用（非必需）
        return self

    # 获取下载文件路径
    def getPath(self):
        return self._abs_path

    # 另一种方式获取路径
    def __str__(self):
        return self.getPath()

    # 锁定文件为只读
    def lock_to_read(self):
        os.chmod(self._abs_path, stat.S_IREAD)

    # 解除文件只读
    def unlock_to_read(self):
        os.chmod(self._abs_path, stat.S_IWRITE)

    # 判断文件是否只读
    def is_only_read(self):
        try:
            with open(self._abs_path, "r+") as fr:
                return False
        except IOError as e:
            if "[Errno 13] Permission denied" in str(e):
                return True
            else:
                logger.error(str(e))
                return False


def sort_path(path_str):
    result = '/.mapper'
    for s in str(path_str):
        result = result + '/' + s
    return result


# 工厂模式获取实例
def get_cell(file_name, remote_path, read_only):
    return cell(file_name=file_name, remote_path=remote_path, read_only=read_only)
