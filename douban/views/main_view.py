#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from base_view import Cli
import subprocess
from colorset.colors import color_func  # colors
from dal.dal_main import MainDal


class Win(Cli):
    """窗体"""

    def __init__(self, data):
        super(Win, self).__init__()
        self.data = data
        self.displayline = data.channel

        self.display_lines = ''  # 展示所有的行
        self.disable = False  # 设置显示失效

    def set_dal(self):
        dal = MainDal(self.data)
        self.c = dal.c  # 主题
        self.set_title(dal.title)
        self.set_love(dal.love)
        self.set_prefix_selected(dal.prefix_selected)
        self.set_prefix_deselected(dal.prefix_deselected)
        self.set_suffix_selected(dal.suffix_selected)
        self.set_suffix_deselected(dal.suffix_deselected)
        self.set_lines(dal.lines)

    def set_disable(self):
        self.disable = True

    def display(self):
        if not self.disable:
            self.set_dal()
            self.make_display_lines()
            for i in self.display_lines:
                print i

    def make_display_lines(self):
        """
        生成输出行

        注意: 多线程终端同时输出会有bug, 导致起始位置偏移
        """
        self.screen_height, self.screen_width = self.linesnum()  # 屏幕显示行数
        subprocess.call('clear', shell=True)  # 清屏

        display_lines = ['\n\r']
        display_lines.append(self._title + '\r')

        top = self.topline
        bottom = self.topline + self.screen_height + 1

        for index, i in enumerate(self._lines[top:bottom]):
            # 箭头指向
            if index == self.markline:
                prefix = self._prefix_selected
                i = color_func(self.c['LINE']['highlight'])(i)
            else:
                prefix = self._prefix_deselected
            # 选择频道
            if index + self.topline == self.displayline:
                suffix = self._suffix_selected
            else:
                suffix = self._suffix_deselected
            line = '%s %s %s' % (prefix, i, suffix)
            line = color_func(self.c['LINE']['line'])(line)

            display_lines.append(line + '\r')  # 为什么加\r,我不知道,如果不加会出bug
        self.display_lines = display_lines
