from dophon.orm import db_obj


def init_orm_manager():
    manager = db_obj.OrmManager()
    return manager


manager = init_orm_manager()
db_obj.init_tables_in_db(manager, ['user', 'dept_info'])

while True:
    try:
        cmd = input('请输入表名:')
        obj = eval('manager.' + cmd + '()')
        print(obj)
        # for attr in dir(obj):
        #     print(attr, ":", eval("obj." + attr))
        cmd = input('请输入参数名:')
        field = eval('obj.' + cmd)
        print(field)
        print('修改参数值')
        exec('obj.' + cmd + ' = \'修改后参数值\'')
        field = eval('obj.' + cmd)
        print(field)
    except Exception as e:
        raise e
        print(e)
