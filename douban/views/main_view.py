#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from base_view import Cli
import subprocess
from colorset.colors import color_func  # colors
import getch
import Queue
from threading import Condition, Thread


class Win(Cli):
    '''窗体及播放控制'''

    def __init__(self):
        self.display_lines = ''
        self.queue = Queue.Queue(0)
        self.condition = Condition()
        self.quit = False

        Thread(target=self._controller).start()
        Thread(target=self._watchdog_queue).start()

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

    def diplay(self):
        for i in self.display_lines:
            print i

    def _watchdog_queue(self):
        while not self.quit:
            print 'watchdog_queue'
            self.condition.acquire()
            if self.queue.empty():
                self.condition.wait()

            k = self.queue.get()
            print k
            if k == 'q':
                self.quit = True

            self.condition.release()

    def _controller(self):
        while not self.quit:
            print 'controller'
            k = getch.getch()

            self.condition.acquire()

            self.queue.put(k)

            self.condition.notify()
            self.condition.release()
