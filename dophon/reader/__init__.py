# coding: utf-8
import xml.dom.minidom
import re

"""
xml读取工具
author:CallMeE
date:2018-06-01
"""


class Mapper:
    _data = {}

    def sortTags(self, file: str, tree, name):
        tags = tree.getElementsByTagName(name)
        data = self._data
        file_list = file.split('/')
        file_name = re.sub('\\..*', '', file_list[len(file_list) - 1])
        if file_name not in data:
            data[file_name]={}
        file_cache=data[file_name]
        for tag in tags:
            val = tag.childNodes[0].data
            attr = tag.getAttribute("id")
            file_cache[attr] = val

    def openDom(self, file):
        # 使用minidom解析器打开 XML 文档
        DOMTree = xml.dom.minidom.parse(file)
        tags = DOMTree.documentElement
        # 取出标签(增删查改)
        self.sortTags(file, DOMTree, 'select')
        self.sortTags(file, DOMTree, 'delete')
        self.sortTags(file, DOMTree, 'insert')
        self.sortTags(file, DOMTree, 'update')

    def getTree(self):
        return self._data
