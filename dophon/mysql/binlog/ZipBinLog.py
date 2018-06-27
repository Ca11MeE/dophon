# coding: utf-8
import re, uuid, zlib

"""
binlog工具
author:CallMeE
date:2018-06-01
"""


def zip_as_bin(file):
    f = open(file, 'r', encoding='utf8')
    bstr = f.read()
    # 去除注释与空格,换行等
    bstr = re.sub('\\s+', ' ', re.sub('<!--.*-->', ' ', bstr))
    # 压缩内容
    z_s = zip_str(bstr)
    bs = []
    for b in str.encode(bstr):
        bs.append(b)
    # 返回唯一标识值(文件存储用文件名原子的uuid,文件标识用压缩内容原子的uuid)
    return uuid.uuid3(uuid.NAMESPACE_DNS, bstr)


# 暂时弃用
def bindigits(n, bits):
    s = bin(n & int("1" * bits, 2))[2:]
    return ("{0:0>%s}" % (bits)).format(s)


def zip_str(string):
    # 压缩内容
    z_result = zlib.compress(string.encode(encoding='utf8'))
    return z_result


def un_zip_str(string):
    # 解压内容
    un_z_result = zlib.decompress(string).decode(encoding='utf8')
    return un_z_result
