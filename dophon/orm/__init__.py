import types


class OrmManager:
    def add_orm_obj(self, table_obj: object):
        if 'table_name' in table_obj:
            # 添加表名单位
            table_name = table_obj['table_name']
            getter_module_code = compile('def ' + table_name + '(): return self.' + table_name, '', 'exec')
            function_code = [c for c in getter_module_code.co_consts if isinstance(c, types.CodeType)][0]
            getter_method = types.FunctionType(function_code, {})
            setattr(self, table_name, property(fget=getter_method))
        else:
            raise Exception('插入对象异常')

    local = locals()

    def print_local(self):
        print(self.local)


manager = OrmManager()
manager.add_orm_obj({
    'table_name': 'demo_table_name'
})
print(manager.demo_table_name)
