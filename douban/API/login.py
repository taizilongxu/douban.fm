#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import getpass
import requests
import json
from json_utils import decode_dict


def win_login():
    """登陆界面"""
    email = raw_input('Email: ')
    password = getpass.getpass('Password: ')
    return email, password


def request_token():
    """通过帐号,密码请求token,返回一个dict"""
    email, password = win_login()
    post_data = {
        'app_name': 'radio_desktop_win',
        'version': '100',
        'email': email,
        'password': password
    }
    s = requests.post('http://www.douban.com/j/app/login', post_data)
    return json.loads(s.text, object_hook=decode_dict)
