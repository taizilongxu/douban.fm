#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from base_view import Cli
import os
from colorset.colors \
    import red, green, on_cyan, on_light_red, color_func  # colors


class Win(Cli):
    '''窗体及播放控制'''
    RATE = ['★'*i for i in range(1, 6)]  # 歌曲评分
    PRO = on_light_red(' PRO ')

    def __init__(self, douban):
        # 线程锁
        self.lock_start = False  # 播放锁,play之前需要加
        self.lock_rate = False   # 加心锁
        self.lock_loop = False   # 循环锁
        self.lock_muted = False  # 静音锁
        self.lock_pause = True   # 暂停锁
        self.q = False           # 退出
        self.songtime = 0        # 歌曲时间
        self.playingsong = None  # 当前播放歌曲

        # state  0    1   2    3       4
        #        main lrc help history quit
        self.state = 0

        self.history = db_config.history

        self.douban = douban

        # default volume
        self._volume = douban.login_data['volume']

        # player controler
        self._player_exit_event = threading.Event()
        self.player = player.MPlayer(self._player_exit_event, self._volume)

        # 快捷键配置
        self.KEYS = db_config.keys

        # 桌面通知
        self.noti = notification.Notify()

        # 存储歌曲信息
        self.lines = self.douban.channels
        self._channel = self.douban.login_data['channel']
        self.playingsong = None
        self.playlist = None
        self.find_lrc = False
        self.lrc_dict = {}  # 歌词

        super(Win, self).__init__(self.lines)

        self.TITLE += color_func(self.c['TITLE']['doubanfm'])(' Douban Fm ')

        self.TITLE += '\ ' + \
            color_func(self.c['TITLE']['username'])(self.douban.login_data['user_name']) + \
            ' >>\r'

        # 启动自动播放
        self.markline = self.displayline = self._channel
        self.lock_start = True
        self.SUFFIX_SELECTED = '正在加载请稍后...'
        self.display()

        self.thread(self.play)          # 播放控制
        self.thread(self.watchdog)      # 播放器守护线程
        self.thread(self.display_time)  # 时间显示
        self.run()

    def make_display_lines(self):
        """
        生成输出行
        """
        self.screen_height, self.screen_width = self.linesnum()  # 屏幕显示行数
        subprocess.call('clear', shell=True)  # 清屏

        display_lines = ['\n']
        display_lines.append(self.TITLE)

        top = self.topline
        bottom = self.topline + self.screen_height + 1

        for index, i in enumerate(self.__lines[top:bottom]):
            # 箭头指向
            if index == self.markline:
                prefix = self.__cli_prefix_selected
                i = color_func(self.c['LINE']['highlight'])(i)
            else:
                prefix = self.__cli_prefix_deselected
            # 选择频道
            if index + self.topline == self.displayline:
                suffix = self.__cli_suffix_selected
            else:
                suffix = self.__cli_suffix_deselected
            line = '%s %s %s' % (prefix, i, suffix)
            line = color_func(self.c['LINE']['line'])(line)

            display_lines.append(line + '\r')  # 为什么加\r,我不知道,如果不加会出bug
        self.display_lines = display_lines


