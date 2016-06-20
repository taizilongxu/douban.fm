#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from pycookiecheat import chrome_cookies
from termcolor import colored
import requests
import getpass
import json

from doubanfm.API.json_utils import decode_dict
from doubanfm.exceptions import APIError

EMAIL_INFO = colored('➔', 'red') + colored(' Email: ', 'green')
PASS_INFO = colored('➔', 'red') + colored(' Password: ', 'green')
CAPTCHA_INFO = colored('➔', 'red') + colored(' Solution: ', 'green')
ERROR = colored('(╯‵□′)╯︵┻━┻: ', 'red')

HEADERS = {"User-Agent": "Paw/2.2.5 (Macintosh; OS X/10.11.1) GCDHTTPRequest"}


def win_login():
    """登陆界面"""
    email = raw_input(EMAIL_INFO)
    password = getpass.getpass(PASS_INFO)
    captcha_id = get_captcha_id()
    get_capthca_pic(captcha_id)
    file = '/tmp/captcha_pic.jpg'
    try:
        from subprocess import call
        from os.path import expanduser
        call([expanduser('~') + '/.iterm2/imgcat', file])
    except:
        import webbrowser
        webbrowser.open('file://' + file)
    captcha_solution = raw_input(CAPTCHA_INFO)
    return email, password, captcha_solution, captcha_id


def request_token():
    """
    通过帐号,密码请求token,返回一个dict
    {
    "user_info": {
        "ck": "-VQY",
        "play_record": {
            "fav_chls_count": 4,
            "liked": 802,
            "banned": 162,
            "played": 28368
        },
        "is_new_user": 0,
        "uid": "taizilongxu",
        "third_party_info": null,
        "url": "http://www.douban.com/people/taizilongxu/",
        "is_dj": false,
        "id": "2053207",
        "is_pro": false,
        "name": "刘小备"
    },
    "r": 0
    }
    """
    while True:
        email, password, captcha_solution, captcha_id = win_login()
        options = {
            'source': 'radio',
            'alias': email,
            'form_password': password,
            'captcha_solution': captcha_solution,
            'captcha_id': captcha_id,
            'task': 'sync_channel_list'
        }
        r = requests.post('https://douban.fm/j/login', data=options, headers=HEADERS)
        req_json = json.loads(r.text, object_hook=decode_dict)
        if req_json['r'] == 0:
            post_data = {
                # will not save
                'liked': req_json['user_info']['play_record']['liked'],
                'banned': req_json['user_info']['play_record']['banned'],
                'played': req_json['user_info']['play_record']['played'],
                'is_pro': req_json['user_info']['is_pro'],
                'user_name': req_json['user_info']['name'],

                # to save
                'cookies': r.cookies,
                'valume': 50,
                'channel': 0,
                'theme_id': 0
            }
            return post_data

        print req_json['err_msg']
        print ERROR + req_json['err_msg']


def get_captcha_id():
    try:
        r = requests.get('https://douban.fm/j/new_captcha', headers=HEADERS)
        r.raise_for_status()
        return r.text.strip('"')
    except Exception as e:
        raise APIError('get captcha id error: ' + str(e))


def get_capthca_pic(captcha_id=None):
    options = {
        'size': 'm',
        'id': captcha_id
    }
    r = requests.get('https://douban.fm/misc/captcha',
                     params=options,
                     headers=HEADERS)
    if r.status_code == 200:
        path = '/tmp/captcha_pic.jpg'
        print 'Download captcha in ' + path
        with open(path, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
    else:
        print "get captcha pic error with http code:" + str(r.status_code)
