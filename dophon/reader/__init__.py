# coding: utf-8
import xml.dom.minidom

"""
xml读取工具
author:CallMeE
date:2018-06-01
"""


class Mapper:
    _data = {}

    def sortTags(self, tree, name):
        tags = tree.getElementsByTagName(name)
        data = self._data
        for tag in tags:
            val = tag.childNodes[0].data
            attr = tag.getAttribute("id")
            data[attr] = val

    def openDom(self, file):
        # 使用minidom解析器打开 XML 文档
        DOMTree = xml.dom.minidom.parse(file)
        tags = DOMTree.documentElement
        # 取出标签(增删查改)
        self.sortTags(DOMTree, 'select')
        self.sortTags(DOMTree, 'delete')
        self.sortTags(DOMTree, 'insert')
        self.sortTags(DOMTree, 'update')

    def getTree(self):
        return self._data

