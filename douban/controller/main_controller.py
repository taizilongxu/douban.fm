#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import getch
import functools
import Queue
from threading import Thread
from views import main_view


class MainController(object):
    """
    按键控制
    """

    def __init__(self, player, data):
        # 接受player, data, view
        self.player = player
        self.data = data
        self.view = main_view.Win(self.data)

        self.player.start_queue(self)
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
        return self.data.playlist.get_song()

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
            if k == 'q':  # 退出
                self.player.quit()
                self.quit = True
                self.switch_queue.put('quit')
            elif k == ' ':
                self.set_channel()
                self.player.start_queue(self)

            elif k == 'o':  # 歌词
                self.quit = True
                self.switch_queue.put('lrc')

            elif k == 'k':  # 向下
                self.up()
            elif k == 'j':  # 向上
                self.down()
            elif k == 'G':
                self.go_bottom()
            elif k == 'g':
                self.go_top()

            elif k == 'p':  # 暂停
                self.player.pause()
            elif k == 'n':  # 下一首
                self.player.next()
            elif k == '-':  # 增大音量
                self.player.set_volume(50)
            elif k == '+':  # 减小音量
                self.player.set_volume(100)

    def _controller(self):
        """
        接受按键, 存入queue
        """
        while not self.quit:
            k = getch.getch()
            self.queue.put(k)
            if k == 'o' or k == 'q':
                break
