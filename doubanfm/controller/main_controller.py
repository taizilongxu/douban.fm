#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import functools
import logging
import Queue
from threading import Thread

from doubanfm import getch
from doubanfm.views import main_view

logger = logging.getLogger('doubanfm')


class MainController(object):
    """
    主界面控制:

    提供run方法以调用该控制
    run方法启动三个进程:
        1. _controller: 提供按键监听
        2. _watchdog_queue: 操作按键对应的命令
        3. _watchdog_time: 标题行需要显示歌曲播放进度

    """

    def __init__(self, player, data):
        # 接受player, data
        self.player = player
        self.data = data
        self.keys = data.keys
        self.view = main_view.Win(self.data)  # 绑定view

        self.player.start_queue(self, data.volume)
        self.queue = Queue.Queue(0)

    def run(self, switch_queue):
        """
        每个controller需要提供run方法, 来提供启动
        """
        self.switch_queue = switch_queue
        self.quit = False

        Thread(target=self._controller).start()
        Thread(target=self._watchdog_queue).start()
        Thread(target=self._watchdog_time).start()

    def display(func):
        @functools.wraps(func)
        def _func(self):
            tmp = func(self)
            if self.view:
                self.view.display()
            return tmp
        return _func

    @display
    def get_song(self):
        """
        切换歌曲时刷新
        """
        return self.data.get_song()

    @property
    def playingsong(self):
        return self.data.playingsong

    @display
    def up(self):
        self.view.up()

    @display
    def down(self):
        self.view.down()

    @display
    def go_bottom(self):
        self.view.go_bottom()

    @display
    def go_top(self):
        self.view.go_top()

    @display
    def set_channel(self):
        self.data.channel = self.view.set_channel()  # 获取view里的channel索引
        self.data.playlist.set_channel(self.data.channel)  # 设置API里的channel

    def set_url(self):
        '''打开豆瓣网页'''
        import webbrowser
        url = "http://music.douban.com" + \
            self.data.playingsong['album'].replace('\/', '/')
        webbrowser.open(url)

    def _watchdog_time(self):
        """
        标题时间显示
        """
        while not self.quit:
            import time
            self.data.time = self.player.time_pos
            self.view.display()
            time.sleep(1)

    def _watchdog_queue(self):
        """
        从queue里取出字符执行命令
        """
        while not self.quit:
            k = self.queue.get()
            if k == self.keys['QUIT']:  # 退出
                self.quit = True
                self.switch_queue.put('quit')
            elif k == self.keys['BYE']:
                self.data.bye()
                self.player.start_queue(self)
            elif k == ' ':  # 播放该频道
                self.set_channel()
                self.player.start_queue(self)
            elif k == self.keys['LOOP']:  # 单曲循环
                self.data.loop = False if self.data.loop else True
                self.player.loop()
            elif k == self.keys['RATE']:  # 加心/去心
                self.data.song_like = False if self.data.song_like else True
                if self.data.song_like:
                    self.data.set_song_like()
                else:
                    self.data.set_song_unlike()

            elif k == self.keys['OPENURL']:  # 打开当前歌曲豆瓣专辑
                self.set_url()

            elif k == self.keys['LRC']:  # 歌词
                self.quit = True
                self.switch_queue.put('lrc')
            elif k == self.keys['HELP']:
                self.quit = True
                self.switch_queue.put('help')
            elif k == self.keys['HIGH']:  # 高品质音乐
                self.data.netease = False if self.data.netease else True

            # getch will return multiple ASCII codes for arrow keys
            # A, B, C, D are the first code of UP, DOWN, LEFT, RIGHT
            elif k == self.keys['UP'] or k == 'B':  # 向下
                self.up()
            elif k == self.keys['DOWN'] or k == 'A':  # 向上
                self.down()
            elif k == self.keys['BOTTOM']:
                self.go_bottom()
            elif k == self.keys['TOP']:
                self.go_top()

            elif k == self.keys['PAUSE']:  # 暂停
                self.data.pause = False if self.data.pause else True
                self.player.pause()
            elif k == self.keys['NEXT']:  # 下一首
                self.player.next()

            elif k == '-' or k == '_':  # 减小音量
                self.data.change_volume(-1)
                logger.info(self.data.volume)
                self.player.set_volume(self.data.volume)
            elif k == '+' or k == '=':  # 增大音量
                self.data.change_volume(1)
                self.player.set_volume(self.data.volume)
            elif k == self.keys['MUTE']:  # 静音
                if self.data.mute:
                    self.data.volume = self.data.mute
                    self.data.mute = False
                    self.player.set_volume(self.data.volume)
                else:
                    self.data.mute = self.data.volume
                    self.data.volume = 0
                    self.player.set_volume(0)

            elif k in ['1', '2', '3', '4']:  # 主题选取
                self.data.set_theme_id(int(k) - 1)

    def _controller(self):
        """
        接受按键, 存入queue
        """
        while not self.quit:
            k = getch.getch()
            self.queue.put(k)
            if k == 'o' or k == 'q' or k == 'h':
                break
