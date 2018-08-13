# coding: utf-8
import re
from dophon import logger

"""
sql分页工具(自带正则寻值)

(不区分大小写)
*num* ----->页码
*size* ------>页容

待实现:
1.参照mybatis的pagehelper


author:CallMeE
date:2018-06-01
"""

logger.inject_logger(globals())


# 打包分页信息
def pkg_page_info(page_num=1, page_size=1, page_model=[]):
    if not page_model:
        return {'page_num': locals()['page_num'], 'page_size': locals()['page_size']}
    else:
        page_info = {}
        # 选取对应key写入数据
        for key in page_model:
            if re.match('.*[nN][uU][mM].*', string=key):
                page_info[key] = page_num
            if re.match('.*[sS][iI][zZ][eE].*', string=key):
                page_info[key] = page_size
        return page_info


# 解包分页信息
def depkg_page_info(page_info):
    for key in page_info:
        if re.match('.*[nN][uU][mM].*', string=key):
            _page_num = page_info[key]
        if re.match('.*[sS][iI][zZ][eE].*', string=key):
            _page_size = page_info[key]
    return 'limit ' + str((int(_page_num) - 1) * int(_page_size)) + ',' + str(_page_size)
