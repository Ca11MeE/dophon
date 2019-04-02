import re


def to_dict(obj: object) -> dict:
    result = {}
    for name in dir(obj):
        if re.match('__.*__', name):
            continue
        else:
            result[name] = getattr(obj, name)
    return result


def to_lower_camel(name: str):
    result = []
    str_len = len(name)
    for c_index in range(str_len):
        c = name[c_index]
        if c.islower():
            result.append(c)
            continue
        if (c_index + 1) < str_len and name[c_index + 1].islower():
            __append = c.lower()
        else:
            __append = c
        if c_index <= 0:
            result.append(__append)
            continue
        result.append(f'_{__append}' if __append.islower() else f'{__append}')
    return ''.join(result)
