from flask import Response
from flask import jsonify

"""
框架自身返回结果类
"""


class JsonResult:
    """
    json类型返回结果类
    """
    __body = {}

    default_mimetype = 'application/json'

    def __init__(self, event=200, data={}, msg=''):
        self.__status = event
        self.__body['event'] = str(event)
        self.__body['data'] = str(data)
        self.__body['msg'] = str(msg)

    def as_res(self):
        return jsonify(self.__body), self.__status


class XmlResult:
    """
    XML类型返回结果类
    """
    __dom = '<root>'

    default_mimetype = 'application/xml'

    def __init__(self, event=200, data={}, msg=''):
        self.__status = event
        self.__dom = self.__dom + '<event>\n' + str(event) + '\n</event>\n'
        self.__dom = self.__dom + '<data>\n' + self.parse_to_node(data) + '\n</data>\n'
        self.__dom = self.__dom + '<msg>\n' + str(msg) + '\n</msg>\n'
        self.__dom= self.__dom + '</root>'

    def parse_to_node(self, data):
        nodes = []
        if isinstance(data, dict):
            for k, v in data.items():
                nodes.append(
                    '<' + str(k) + '>\n' + (str(v) if not isinstance(v, dict) else self.parse_to_node(v)) + '\n</' + str(
                        k) + '>\n')
        elif isinstance(data, list):
            for index in range(len(data)):
                nodes.append(
                    '<' + str(index) + '>\n' + (
                        str(data[index]) if not isinstance(data[index], dict) else self.parse_to_node(
                            data[index])) + '\n</' + str(
                        index) + '>\n')
        else:
            nodes.append(str(data))
        return '\n'.join(nodes)

    def as_res(self):
        return Response(str(self.__dom), mimetype=self.default_mimetype, status=self.__status)
