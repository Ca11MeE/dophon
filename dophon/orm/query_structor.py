"""
查询语句结构映射

结构:
select
<Field>
from
<tables>
where
<param_dicts>
<sort_param>
"""

class Fields:
    """
    查询语句查询列参数类
    """
    def __init__(self,*args,**kwargs):
        print(*args)
        print(**kwargs)

class Struct():
    """
    查询语句结构类
    """
    pass

if '__main__'==__name__:
    import dophon.orm as orm
    manager=orm.init_orm_manager(['user'])
    user=manager.user()
    Fields(str(user.user_id),str(user.info_id))
    print(user([]))