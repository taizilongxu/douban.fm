#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import os
import json
import ConfigParser
import cPickle as pickle


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


def init_config():
    '''
    检查配置文件
    '''
    if not os.path.exists(PATH_CONFIG):
        print '\033[31m♥\033[0m Get default config [\033[32m OK \033[0m]'
        with open(PATH_CONFIG, 'w') as F:
            F.write(CONFIG)
    else:
        print '\033[31m♥\033[0m Get local config [\033[32m OK \033[0m]'


def get_config(keys):
    '''
    获取配置并检查是否更改
    '''
    config = ConfigParser.ConfigParser()
    with open(PATH_CONFIG, 'r') as cfgfile:
        config.readfp(cfgfile)
        options = config.options('key')
        for option in options:
            option = option.upper()
            if option in keys:
                keys[option] = config.get('key', option)


def get_history():
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
