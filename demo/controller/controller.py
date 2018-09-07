from dophon.mysql import *


class TestController:
    def __init__(self):
        self.cursor = pg_obj(path='/mappers/demo_mapper.xml', auto_fix=True)

    def test_page_select(self):
        result = self.cursor.pageable_exe_sql(methodName='page_select', pageInfo={
            'num': 1,
            'size': 3
        })
        print(result)
        return result
