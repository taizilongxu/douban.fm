#!/usr/bin/env python
# encoding: utf-8
import os
import ConfigParser

CONFIG_PATH = os.path.expanduser("~/.doubanfm_config")
CONFIG = \
'''
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
    if not os.path.exists(CONFIG_PATH):
        print '\033[31m♥\033[0m Get default config [\033[32m OK \033[0m]'
        with open(CONFIG_PATH, 'w') as F:
            F.write(CONFIG)
    else:
        print '\033[31m♥\033[0m Get local config [\033[32m OK \033[0m]'

def get_config(keys):
    '''
    获取配置并检查是否更改
    '''
    config = ConfigParser.ConfigParser()
    with open(CONFIG_PATH, 'r') as cfgfile:
        config.readfp(cfgfile)
        options = config.options('key')
        for option in options:
            option = option.upper()
            if option in keys:
                keys[option] = config.get('key', option)
