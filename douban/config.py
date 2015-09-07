#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import os
import ConfigParser
import cPickle as pickle
import logging
from colorset import theme
from API.login import request_token

logger = logging.getLogger('doubanfm')  # get logger

THEME = ['default', 'larapaste', 'monokai', 'tomorrow']
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
    """Docstring for Config. """

    def __init__(self):
        # TODO 加入config里
        self.__theme = 'tomorrow'

    @property
    def login_data(self):
        if os.path.exists(PATH_TOKEN):
            # 使用上次登录保存的token
            with open(PATH_TOKEN, 'r') as f:
                login_data = pickle.load(f)
            print '\033[31m♥\033[0m Get local token - Username: \033[33m%s\033[0m' %\
                login_data['user_name']
        else:
            # 未登陆
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

    @property
    def keys(self):
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

    @property
    def history(self):
        try:
            with open(PATH_HISTORY, 'r') as f:
                history = pickle.load(f)
        except IOError:
            history = []
        return history

    @property
    def theme(self):
        """
        THEME = ['default', 'larapaste', 'monokai', 'tomorrow']
        """
        # Todo
        return getattr(theme, self.__theme)

    @theme.setter
    def theme(self, value):
        """
        :param value: 0, 1, 2, 3
        """
        self.__theme = THEME[value]

    @staticmethod
    def save_config(history, login_data):
        """
        存储历史记录和登陆信息
        """
        with open(PATH_TOKEN, 'w') as f:
            pickle.dump(login_data, f)

        with open(PATH_HISTORY, 'w') as f:
            pickle.dump(history, f)


db_config = Config()
