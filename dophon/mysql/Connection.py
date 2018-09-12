# coding: utf-8
# 连接包装类
import pymysql
from dophon import properties
from dophon import logger

"""
mysql连接实例(半成品)

待实现:;
1.配置文件配置连接属性
author:CallMeE
date:2018-06-01
"""

logger.inject_logger(globals())

namespace = [
    '_host',
    '_user',
    '_password',
    '_database',
    '_port',
    '_unix_socket',
    '_charset',
    '_sql_mode',
    '_read_default_file',
    '_conv',
    '_use_unicode',
    '_client_flag',
    '_cursorclass',
    '_init_command',
    '_connect_timeout',
    '_ssl',
    '_read_default_group',
    '_compress',
    '_named_pipe',
    '_no_delay',
    '_autocommit',
    '_db',
    '_passwd',
    '_local_infile',
    '_max_allowed_packet',
    '_defer_connect',
    '_auth_plugin_map',
    '_read_timeout',
    '_write_timeout',
    '_bind_address',
    '_binary_prefix'
]


class Connection:
    '''
    数据库连接参数默认为连接本地root账户

    目前只支持配置参数以及默认值:
    _host = 'localhost'
    _user = 'root'
    _password = 'root'
    _database = None
    '''
    _host = properties.pydc_host
    _user = properties.pydc_user
    _password = properties.pydc_password
    _database = properties.pydc_database
    _port = properties.pydc_port

    def __init__(self, __host=_host, __port=_port, __user=_user, __password=_password, __database=_database,
                 __charset='utf8'):
        self._db = pymysql.connect(host=__host, port=__port, user=__user, password=__password, database=__database,
                                   charset=__charset)

    def getConnect(self):
        return self._db

    def testConn(self):
        try:
            self._db.ping()
            return True
        except:
            return False

    def reConn(self):
        self._db = pymysql.connect(self._host, self._port, self._user, self._pwd, self._db, charset='utf8')