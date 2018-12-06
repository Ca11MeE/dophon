import re


def to_dict(obj: object) -> dict:
    result = {}
    for name in dir(obj):
        if re.match('__.*__', name):
            continue
        else:
            result[name] = getattr(obj, name)
    return result
