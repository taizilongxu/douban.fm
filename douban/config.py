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

LOGO = '''
[38;5;202m⡇       ⡆  ⡀    ⣄       ⣆       ⡄⢀      ⢀⡄          ⡄              ⢠⡇           (B[m
[38;5;214m⡇      ⢰⡇  ⣿    ⡗⢤      ⡏⡆    ⢸⣼⠘⢾      ⢸⡇ ⡄       ⢰⡇ ⣴   ⣰     ⡀  ⡇⡇       ⢀⢧  (B[m
[38;5;226m⡇      ⢸⢇  ⣿   ⢀⠇⠘⡄     ⡇⡇    ⡇⠁ ⠘⡄  ⢸⡀ ⡎⡇⢰⢹       ⡜⡇⢰⠁⢇ ⢠⢿  ⢸⢆ ⣇  ⡇⡇  ⣄    ⢸⢸  (B[m
[38;5;190m⡇     ⢀⠇⢸  ⡏⡆  ⢸  ⡇⣷   ⢸ ⡇    ⡇   ⡇  ⢸⡇ ⡇⢱⡎⢸    ⡆  ⡇⢸⢸ ⢸ ⢸⠘⡄ ⢸⢸⢀⢿  ⡇⢱⢀ ⣿ ⢸⡀ ⢸⠈⡆ (B[m
[38;5;154m⡇     ⢸ ⢸⢰ ⡇⡇  ⢸  ⣇⠟⡄  ⢸ ⢣   ⣠⠃   ⡇  ⡸⡇⢰⠁⢸⠇⢸ ⡀ ⢰⢹  ⡇⢸⢸ ⠸⡀⢸ ⡇ ⡸⢸⢸⠸⡀⢠⠃⢸⢸⡄⡿⡀⡇⡇ ⢸ ⡇ (B[m
[38;5;82m⡇  ⣦  ⡇ ⢸⢸⣿ ⢱  ⢸  ⢸ ⢣  ⢸ ⢸  ⡜⠈    ⡇⣄ ⡇⢱⢸ ⠘ ⠸⣸⢣ ⢸⠘⢤⢀⠇⢸⡇  ⡇⡸ ⡇ ⡇ ⣿ ⡇⢸ ⢸⢸⣿ ⠗⠁⢱ ⢸ ⡇ (B[m
[38;5;46m⡇  ⣿  ⡇ ⢸⡇⣿ ⢸  ⡸    ⠘⢄ ⢸ ⢸ ⢠⠃     ⡇⣿ ⡇⠘⡼    ⡿⠸⡀⡇  ⣿ ⢸⡅  ⡇⡇ ⢣ ⡇ ⣿ ⢣⢸ ⢸⡜⠸   ⠸⡀⢸ ⡇ (B[m
[38;5;48m⣧⠒⣴⢹ ⣀⠇ ⠸⡇⢻  ⠱⡀⡅      ⡇⢸  ⡇⢸      ⡇⣿ ⡇ ⠁    ⠇ ⡇⡇  ⢿ ⢸⡇  ⢸⡇ ⠘⡄⡇ ⡟ ⢸⠎ ⢸⡇     ⡇⡇ ⡇⡇(B[m
[38;5;50m⡟ ⠻ ⡿⠹   ⠁⠘   ⣇⠇      ⠈⠇  ⢇⠇      ⢳⠉⣦⠃        ⣷⠁  ⠈  ⠇  ⢸⡇  ⠉⠃      ⢸⡇     ⢸⡇ ⢱⠇(B[m
[38;5;51m⠁   ⠁         ⢻           ⠈       ⢸ ⠏         ⢹         ⠘⠇          ⠈⡇      ⠇ ⠸ (B[m
'''


class Config(object):
    """
    提供默认值
    """

    def __init__(self):
        # TODO 加入config里
        self.__theme = 'tomorrow'
        self.volume = 50
        self.channel = 0
        self.theme_id = 0
        self.user_name = ''

        self.login_data = self.get_login_data()

    def output(args):
        def _deco(func):
            def _func(self):
                print '\033[31m♥\033[0m ' + args,
                tmp = func(self)
                print ' [\033[32m OK \033[0m]'
                return tmp
            return _func
        return _deco

    def get_login_data(self):
        """
        提供登陆的认证

        这里顺带增加了 volume, channel, theme_id 的默认值
        """
        if os.path.exists(PATH_TOKEN):
            # 使用上次登录保存的token
            with open(PATH_TOKEN, 'r') as f:
                login_data = pickle.load(f)
        else:
            # 未登陆
            while True:
                login_data = request_token()
                if login_data['r'] == 0:
                    login_data['volume'] = 50
                    login_data['channel'] = 0
                    login_data['theme_id'] = 0
                    break
                print login_data['err']
                logger.debug(login_data['err'])

        print '\033[31m♥\033[0m Get local token - Username: \033[33m%s\033[0m' %\
            login_data['user_name']
        self.volume = login_data.get('volume', 50)
        self.channel = login_data.get('channel', 0)
        self.theme_id = login_data.get('theme_id', 0)
        self.user_name = login_data.get('user_name', '')
        return login_data

    @property
    @output('Get keys')
    def keys(self):
        '''
        获取配置并检查是否更改
        '''
        if not os.path.exists(PATH_CONFIG):
            with open(PATH_CONFIG, 'w') as F:
                F.write(CONFIG)
        else:
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
        THEME = ['default', 'larapaste', 'monokai', 'tomorrow']
        return getattr(theme, THEME[self.theme_id])

    @theme.setter
    def theme(self, value):
        """
        :param value: 0, 1, 2, 3
        """
        self.theme_id = value

    def save_config(self, volume, channel, theme):
        """
        存储历史记录和登陆信息
        """
        self.login_data['volume'] = volume
        self.login_data['channel'] = channel
        self.login_data['theme_id'] = theme
        with open(PATH_TOKEN, 'w') as f:
            pickle.dump(self.login_data, f)

        # with open(PATH_HISTORY, 'w') as f:
        #     pickle.dump(history, f)


db_config = Config()
