from dophon.mysql import Connection
from dophon import mysql
import types

tables_in_db = []  # 数据库表名列表
tables_param_list = {}


def init_tables_in_db():
    connect = Connection.Connection().getConnect()
    cursor = connect.cursor()
    cursor.execute('SHOW TABLES')
    connect.commit()
    # 整理数据表名列表
    for tup_item in cursor.fetchall():
        tables_in_db.append(tup_item[0])
    connect.close()


def init_table_param(table_name):
    connect = Connection.Connection().getConnect()
    cursor = connect.cursor()
    cursor.execute('DESC ' + table_name)
    connect.commit()
    titles = cursor.description
    values = cursor.fetchall()
    result = mysql.sort_result(values, titles, [])
    tables_param_list[table_name] = result
    connect.close()


# init_tables_in_db()
# for table_name in tables_in_db:
#     init_table_param(table_name)
# init_table_param(tables_in_db[0])
# print(tables_param_list)

def inject_method(arg_name):
    # compile setter method
    setter_name = 'set_' + arg_name
    setter_module_code = compile('def ' + setter_name + '(): return ' + setter_name, setter_name, 'exec')
    function_code = [c for c in setter_module_code.co_consts if isinstance(c, types.CodeType)][0]
    setter_method = types.FunctionType(function_code, {})

    # compile getter method
    getter_name = 'get_' + arg_name
    getter_module_code = compile('def ' + getter_name + '(): return ' + getter_name, getter_name, 'exec')
    function_code = [c for c in getter_module_code.co_consts if isinstance(c, types.CodeType)][0]
    getter_method = types.FunctionType(function_code, {})


def set_arg_demo():
    pass


class test():
    local = locals()

    def set_arg(self, value):
        self._arg = value

    def get_arg(self):
        return self._arg

    def print_local(self):
        print(self.local)

    _arg = property(get_arg, set_arg)

    @property
    def prop_arg(self):
        return 'prop_arg'

    @prop_arg.setter
    def prop_arg(self):
        pass

    @prop_arg.getter
    def prop_arg(self):
        pass


test = test()
test.print_local()
