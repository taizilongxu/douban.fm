#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import os
import ConfigParser
import cPickle as pickle
import logging
import time

from doubanfm.API.login import request_token

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
HELP = h
HIGH = i
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
    'HELP': 'h',
    'HIGH': 'i'
    }


class Config(object):
    """
    提供默认值
    """

    def __init__(self):
        self.volume = 50  # 音量
        self.channel = 0  # 频道
        self.theme_id = 0  # 主题
        self.user_name = ''  # 用户名
        self.netease = False  # 是否使用网易320k音乐播放
        self.run_times = 0  # 登陆次数
        self.last_time = time.time()  # 当前登陆时间戳
        self.total_time = 0  # 总共登陆时间

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

        这里顺带增加了 volume, channel, theme_id , netease, run_times的默认值
        """
        if os.path.exists(PATH_TOKEN):
            # 使用上次登录保存的token
            with open(PATH_TOKEN, 'r') as f:
                login_data = pickle.load(f)
        else:
            # 未登陆
            login_data = request_token()

        self.get_default_set(login_data)
        self.get_user_states(login_data)

        return login_data

    def get_default_set(self, login_data):
        """
        记录退出时的播放状态
        """
        self.user_name = login_data.get('user_name', '')
        print '\033[31m♥\033[0m Get local token - Username: \033[33m%s\033[0m' %\
            login_data['user_name']

        self.channel = login_data.get('channel', 0)
        print '\033[31m♥\033[0m Get channel [\033[32m OK \033[0m]'

        self.volume = login_data.get('volume', 50)
        print '\033[31m♥\033[0m Get volume [\033[32m OK \033[0m]'

        self.theme_id = login_data.get('theme_id', 0)
        print '\033[31m♥\033[0m Get theme [\033[32m OK \033[0m]'

        self.netease = login_data.get('netease', False)

    def get_user_states(self, login_data):
        """
        统计用户信息
        """
        self.run_times = login_data.get('run_times', 0)
        self.total_time = login_data.get('total_time', 0)

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

    def save_config(self, volume, channel, theme, netease):
        """
        存储历史记录和登陆信息
        """
        self.login_data['volume'] = volume
        self.login_data['channel'] = channel
        self.login_data['theme_id'] = theme
        self.login_data['netease'] = netease
        self.login_data['run_times'] = self.run_times + 1
        self.login_data['last_time'] = self.last_time
        self.login_data['total_time'] = self.total_time +\
                                        time.time() - self.last_time
        with open(PATH_TOKEN, 'w') as f:
            pickle.dump(self.login_data, f)

        # with open(PATH_HISTORY, 'w') as f:
        #     pickle.dump(history, f)


db_config = Config()
