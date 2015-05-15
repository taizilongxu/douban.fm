#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import os
import json
import ConfigParser
import cPickle as pickle
from douban_token import request_token


PATH_CONFIG = os.path.expanduser("~/.doubanfm_config")
PATH_HISTORY = os.path.expanduser('~/.doubanfm_history')
PATH_TOKEN = os.path.expanduser('~/.doubanfm_token')
CONFIG = '''
[key]
UP = k
DOWN = j
TOP = g
BOTTOM = G
OPENURL = w
RATE = r
NEXT = n
BYE = b
QUIT = q
PAUSE = p
LOOP = l
MUTE = m
LRC = o
'''
KEYS = {
    'UP': 'k',
    'DOWN': 'j',
    'TOP': 'g',
    'BOTTOM': 'G',
    'OPENURL': 'w',
    'RATE': 'r',
    'NEXT': 'n',
    'BYE': 'b',
    'QUIT': 'q',
    'PAUSE': 'p',
    'LOOP': 'l',
    'MUTE': 'm',
    'LRC': 'o',
    'HELP': 'h'
    }

class Config(object):
    """Docstring for Congif. """

    def __init__(self):
        """TODO: to be defined. """
        self.history = self.get_history()
        self.keys = self.get_config()
        self.login_data = self.get_token()

    def get_token(self):
        '''登陆douban.fm获取token'''
        if os.path.exists(PATH_TOKEN):
            # 使用上次登录保存的token
            # logger.info("Found existing Douban.fm token.")
            with open(PATH_TOKEN, 'r') as f:
                login_data = pickle.load(f)
            print '\033[31m♥\033[0m Get local token - Username: \033[33m%s\033[0m' %\
                login_data['user_name']
        else:
            # 未登陆
            logger.info('First time logging in Douban.fm.')
            while True:
                login_data = request_token()
                if login_data['r'] == 1:
                    logger.debug(login_data['err'])
                    continue
                login_data.update({'volume': 50,
                                   'channel': 0,
                                   'theme_id': 0})
                break
        return login_data

    def get_config(self):
        '''
        获取配置并检查是否更改
        '''
        if not os.path.exists(PATH_CONFIG):
            print '\033[31m♥\033[0m Get default config [\033[32m OK \033[0m]'
            with open(PATH_CONFIG, 'w') as F:
                F.write(CONFIG)
        else:
            print '\033[31m♥\033[0m Get local config [\033[32m OK \033[0m]'
            config = ConfigParser.ConfigParser()
            with open(PATH_CONFIG, 'r') as cfgfile:
                config.readfp(cfgfile)
                options = config.options('key')
                for option in options:
                    option = option.upper()
                    if option in KEYS:
                        KEYS[option] = config.get('key', option)
        return KEYS

    def get_history(self):
        '''
        获取历史记录
        '''
        try:
            with open(PATH_HISTORY, 'r') as f:
                history = pickle.load(f)
        except IOError:
            history = []
        return history


def set_history(history):
    '''
    保存历史记录
    '''
    with open(PATH_HISTORY, 'w') as f:
        pickle.dump(history, f)


def set_default(volume, channel):
    '''
    保存默认音量和频道
    '''
    with open(PATH_TOKEN, 'r') as f:
        data = pickle.load(f)
        data['volume'] = volume
        data['channel'] = channel
    with open(PATH_TOKEN, 'w') as f:
        pickle.dump(data, f)


def get_default_theme(theme):
    """
    Get default value of a config key
    """
    path = os.path.dirname(__file__) + '/colorset/' + theme + '.json'
    # path = '/Users/limbo/Cloud/cli/douban/colorset/default.json'
    with open(path) as f:
        content = ''.join(f.readlines())
    return json.loads(content)

def local_data():
    local_data = Config()
    return local_data.history, local_data.keys, local_data.login_data
