import re

from build.lib.dophon.orm.db_obj.function_class import OrmObj


class Parseable:

    def read_from_dict(self, d: dict):
        """
        读取字典生成orm对象
        :param d:
        :return:
        """
        for key in d.keys():
            if hasattr(self, key):
                setattr(self, key, d[key])
            else:
                raise Exception('无法转换为' + str(getattr(self, 'table_map_key')) + '类型')

    def copy_to_obj(self, clz: OrmObj):
        res_obj = clz()
        for name in dir(self):
            if re.search('^_.*', name):
                continue
            if name not in dir(res_obj):
                raise Exception('无法复制的类型')
