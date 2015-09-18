#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
豆瓣fm主程序
"""
# local
from player import MPlayer       # player
# import notification             # desktop notification
# from config import db_config    # config
# from colorset.colors import on_light_red, color_func  # colors
import Queue
import logging
import os
from threading import Thread
from model import Playlist, Channel
from config import db_config
from colorset import theme

from controller.main_controller import MainController
from controller.lrc_controller import LrcController
from controller.help_controller import HelpController

# root logger config
logging.basicConfig(
    format="%(asctime)s - \
[%(process)d]%(filename)s:%(lineno)d - %(levelname)s: %(message)s",
    datefmt='%Y-%m-%d %H:%I:%S',
    filename=os.path.expanduser('~/.doubanfm.log'),
    level=logging.INFO
)

# Set up our own logger
logger = logging.getLogger('doubanfm')
logger.setLevel(logging.INFO)


class Data(object):
    """
    所有需要的数据统一在一起
    """

    def __init__(self):
        self.playlist = Playlist()
        self.lines = Channel().lines
        # self.hitory = History()
        self.keys = db_config.keys  # keys
        self.volume = db_config.volume  # 声量
        self.theme_id = db_config.theme_id  # 主题id
        self.channel = db_config.channel  # 当前频道
        self.user_name = db_config.user_name  # 用户名

        self.song_like = False  # 当前歌词是否like
        self.loop = False  # 单曲循环
        self.pro = False  # pro用户
        self.mute = False  # 静音
        self.time = 0  # 时间/秒

    @property
    def theme(self):
        THEME = ['default', 'larapaste', 'monokai', 'tomorrow']
        return getattr(theme, THEME[self.theme_id])

    def set_theme_id(self, value):
        self.theme_id = value

    @property
    def lrc(self):
        return self.playlist.get_lrc()

    @property
    def playingsong(self):
        return self.playlist.get_playingsong()

    def get_song(self):
        playingsong = self.playlist.get_song()
        self.song_like = playingsong['like']
        return playingsong

    def set_song_like(self):
        self.song_like = True
        self.playlist.set_song_like()

    def set_song_unlike(self):
        self.song_like = False
        self.playlist.set_song_unlike()

    def change_volume(self, increment):
        """调整音量大小"""
        if increment == 1:
            self.volume += 5
        else:
            self.volume -= 5
        self.volume = max(min(self.volume, 100), 0)  # 限制在0-100之间

    def save(self):
        db_config.save_config(self.volume, self.channel, self.theme_id)


class Router(object):
    """
    集中管理view之间的切换
    """

    def __init__(self):
        self.player = MPlayer()
        self.data = Data()

        self.switch_queue = Queue.Queue(0)

        self.view_control_map = {
            'main': MainController(self.player, self.data),
            'lrc': LrcController(self.player, self.data),
            'help': HelpController(self.player, self.data),
            'quit': False
        }

        # 切换线程
        Thread(target=self._watchdog_switch).start()

    def _watchdog_switch(self):
        # init
        self.view_control_map['main'].run(self.switch_queue)

        while not self.view_control_map['quit']:
            key = self.switch_queue.get()
            if key == 'quit':
                self.view_control_map['quit'] = True
            else:
                self.view_control_map[key].run(self.switch_queue)

        # 退出保存信息
        self.data.save()


Router()



# def run(self):
#     '''主交互逻辑 (key event loop)'''
#     while True:
#         self.display()
#         k = getch.getch()
#         if self.state != 1:  # 歌词模式下除了方向键都可以用
#         if k == self.KEYS['HELP']:     # help界面
#             self.state = 2
#             Help(self)
#         elif k == 'e' and self.state == 0:
#             self.state = 3
#             History(self)
#         elif k == self.KEYS['BYE']:      # b不再播放
#             self.set_bye()
#         elif k in ['1', '2', '3', '4']:
#             db_config.theme = int(k) - 1
#             self.reload_theme()


# def main():
#     Win(douban)

# if __name__ == '__main__':
#     main()
