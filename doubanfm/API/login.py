#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import requests
import getpass
import json
from termcolor import colored

from doubanfm.API.json_utils import decode_dict

EMAIL_INFO = colored('➔', 'red') + colored(' Email: ', 'green')
PASS_INFO = colored('➔', 'red') + colored(' Password: ', 'green')
ERROR = colored('(╯‵□′)╯︵┻━┻: ', 'red')

def win_login():
    """登陆界面"""
    email = raw_input(EMAIL_INFO)
    password = getpass.getpass(PASS_INFO)
    return email, password


def request_token():
    """通过帐号,密码请求token,返回一个dict"""
    while True:
        email, password = win_login()
        post_data = {
            'app_name': 'radio_desktop_win',
            'version': '100',
            'email': email,
            'password': password
        }
        s = requests.post('http://www.douban.com/j/app/login', post_data)
        login_data = json.loads(s.text, object_hook=decode_dict)

        if login_data['r'] == 0:
            login_data['volume'] = 50
            login_data['channel'] = 0
            login_data['theme_id'] = 0
            return login_data
        print ERROR + login_data['err']
