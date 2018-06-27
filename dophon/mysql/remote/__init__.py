# coding: utf-8
from dophon.mysql.remote import Cell

"""
远程xml模块工厂
author:CallMeE
date:2018-06-01


# 开启远程xml推荐导入本模块获取实例
# import mysql.remote as remote
"""


# 工厂模式获取远程细胞实例
def getCell(file_name, remote_path, read_only=False):
    return Cell.get_cell(file_name=file_name, remote_path=remote_path, read_only=read_only)