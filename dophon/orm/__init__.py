from dophon.orm import db_obj


def init_orm_manager():
    manager = db_obj.OrmManager()
    db_obj.init_tables_in_db(manager, ['user', 'dept_info'])
    return manager


import datetime

if '__main__' == __name__:
    manager = init_orm_manager()
    user = manager.user()
    # for attr in dir(user):
    #     print(attr, ":", eval("user." + attr))
    user.user_id = 'id'
    user.info_id = 'info_id'
    user.user_name = 'user_name'
    user.user_pwd = 'user_pwd'
    user.user_status = 123
    user.create_time = datetime.datetime.now()
    user.update_time = datetime.datetime.now()
    # for attr in dir(user):
    #     print(attr, ":", eval("user." + attr))
