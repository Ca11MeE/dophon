# coding: utf-8
import re
from dophon import logger
import functools

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
def depkg_page_info(page_info: dict):
    for key in page_info:
        if re.match('.*[nN][uU][mM].*', string=key):
            _page_num = page_info[key]
        if re.match('.*[sS][iI][zZ][eE].*', string=key):
            _page_size = page_info[key]
        return 'limit ' + str(
            0 if (int(_page_num) - 1) * int(_page_size) < 0 else (int(_page_num) - 1) * int(_page_size)) + ',' + str(
            _page_size)


def fix_page_info(page_info: dict):
    """
    修正分页信息
    :param page_info:
    :return:
    """
    for key in page_info:
        if re.match('.*[nN][uU][mM].*', string=key):
            _page_num = page_info[key]
        if re.match('.*[sS][iI][zZ][eE].*', string=key):
            _page_size = page_info[key]
    return {'page_num': _page_num, 'page_size': _page_size}


# 分页装饰器
def pkg_pageobj(f):
    """
    封装结果集为分页信息结果集 -> Pages
    :param f:
    :return:
    """
    print(f)
    def f_args(*args, **kwargs):
        # 执行查询
        result = f(*args, **kwargs)
        # 结果校验
        if isinstance(result, list):
            # 分页信息检查
            if 'pageInfo' in kwargs and kwargs['pageInfo']:
                page_obj = fix_page_info(kwargs['pageInfo'])
                page_obj['list'] = result
                return page_obj
            else:
                logger.error('不存在分页信息')
                return result
        else:
            logger.error('结果不符合分页策略')

    return f_args
