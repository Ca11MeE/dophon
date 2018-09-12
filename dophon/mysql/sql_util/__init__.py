from pymysql import escape_dict, escape_sequence, escape_string

escape_charset = 'utf-8'


def escape(val):
    """
    转义值,防sql注入
    :param val:
    :return:
    """
    if isinstance(val, dict):
        return escape_dict(val, charset=escape_charset)
    elif isinstance(val, (list, set,)):
        return escape_sequence(val, charset=escape_charset)
    else:
        return escape_string(val)
