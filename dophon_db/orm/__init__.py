from dophon_db.orm import db_obj


def init_orm_manager(table_list: list = []):
    manager = db_obj.OrmManager()
    db_obj.init_tables_in_db(manager, table_list)
    return manager


import datetime

if '__main__' == __name__:
    print('初始化orm管理器')
    manager = init_orm_manager(['user'])
    print('获取orm管理器中对应表映射对象')
    user = manager.user()

    user.user_id='111'
    print(user.user_id)
    user.flush()
    print(user.user_id)
    user.user_id='111'
    print(user.user_id)
    user.flush()
    print(user.user_id)
    user.user_id='111'
    print(user.user_id)
    user.flush()
    print(user.user_id)
    user.user_id='111'
    print(user.user_id)
    user.flush()
    print(user.user_id)
    user.user_id='111'
    print(user.user_id)
    user.flush()
    print(user.user_id)



    user.user_id='111'
    print(user.user_id)
    user.flush()
    print(user.user_id)
    user.user_id='111'
    print(user.user_id)
    user.flush()
    print(user.user_id)
    user.user_id='111'
    print(user.user_id)
    user.flush()
    print(user.user_id)


    print('打印对象变量域')
    for attr in dir(user):
        print(attr, ":", eval("user." + attr))
    print('开始对对象赋值')
    user.user_id = 'id'
    user.info_id = 'info_id'
    user.user_name = 'user_name'
    user.user_pwd = 'user_pwd'
    user.user_status = 123
    user.create_time = datetime.datetime.now().strftime('%y-%m-%d')
    user.update_time = datetime.datetime.now().strftime('%y-%m-%d')
    print('对象赋值完毕')
    print('打印对象变量域')
    for attr in dir(user):
        print(attr, ":", eval("user." + attr))
    print('打印对象参数表')
    print(user([]))

    print('user([]):', user([]))
    print("user(['user_id','info_id']):", user(['user_id', 'info_id']))
    print("user.get_field_list():", user.get_field_list())
    print("user.alias('user_table').get_field_list():", user.alias('user_table').get_field_list())

    print(user.where())
    print(user.values())

    user.select()
    user.user_name = '111'
    user.select_one()
    user.select_all()

    user = manager.user()
    user.alias('u').select()
    user.user_name = '111'
    user.alias('us').select_one()
    user.alias('userr').select_all()


    user.user_id='test_id'
    user.info_id='test_info_id'
    user.user_name='test_user_name'
    user.user_pwd='test_user_pwd'
    user.user_status=1
    user.create_time = datetime.datetime.now().strftime('%y-%m-%d')
    user.update_time = datetime.datetime.now().strftime('%y-%m-%d')

    print(user.insert())
    #
    user.user_id = 'test_id'
    user.info_id = 'info_id'
    user.user_name = '柯李艺'
    user.user_pwd = '333'
    user.user_status = 123
    print(user.update(update=['user_name','user_pwd'],where=['user_id']))
    #
    user.user_id = 'test_id'
    user.info_id = 'info_id'
    user.user_name = 'user_name'
    user.user_pwd = 'user_pwd'
    user.user_status = 123
    print(user.delete(where=['user_id']))

    user1=manager.user()
    user2=manager.user()
    print(user1.select())
    user1.user_name='early'
    user1.left_join(user2,['user_id'],['user_id'])
    user1.alias('u1').left_join(user2.alias('u2'),['user_id'],['user_id'])
    # print(user1.exe_join())
    print(user1.select())

    user1 = manager.user()
    print('user1', '---', id(user1))
    user2 = user1.copy_to_obj(manager.user)
    print('user2', '---', id(user2))
    print(user1('user_id'))
    print(user1.user_id)
    user3 = user1.read_from_dict({
        'user_id': '111'
    })
    print('user3', '---', id(user3))
    print(user1('user_id'))
    print(user1.user_id)
    print(user3('user_id'))
