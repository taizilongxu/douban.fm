# -*- coding: utf-8 -*-
import six
from six import iteritems
from six import text_type


def _decode_list(data):
    """
    解析json列表,转换成utf-8
    """
    if six.PY3:
        return data
    rv = []
    for item in data:
        if not isinstance(item, text_type):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        rv.append(item)
    return rv


def decode_dict(data):
    """
    解析json字典,转换成utf-8
    """
    if six.PY3:
        return data
    rv = {}
    for key, value in iteritems(data):
        if isinstance(key, text_type):
            key = key.encode('utf-8')

        if isinstance(value, text_type):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        # no need to recurse into dict, json library will do that
        rv[key] = value
    return rv
