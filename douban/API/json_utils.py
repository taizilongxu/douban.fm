# -*- coding: utf-8 -*-


def _decode_list(data):
    """
    解析json列表,转换成utf-8
    """
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        rv.append(item)
    return rv


def decode_dict(data):
    """
    解析json字典,转换成utf-8
    """
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')

        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        # no need to recurse into dict, json library will do that
        rv[key] = value
    return rv
