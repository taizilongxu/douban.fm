#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
用print设计的滚动终端界面

__cli_prefix_selected:可以指定当前指向行的前缀
__cli_prefix_deselected:暂时没有用,如果想保持选项行一致需要填写和PREFIX_SELECTED一样大小的空格
__cli_suffix_selected:对选中行进行标记
__cli_suffix_deselected:暂时无用
__cli_title:界面标题的设定
'''
#######################################################################
# topline: 屏幕显示最顶
# markline:  > 光标的行数
# displayline: 展示歌曲信息的行数
#######################################################################
#            self.TITLE
#            4 displayline
# markline > 5
#            6
#            7
#            8
#            9
#######################################################################
# topline = 3      # start with 0
# markline = 1
# displayline = 0
#######################################################################

import subprocess
import getch
from config import db_config


class Cli(object):

    def __init__(self, lines):
        self.__lines = lines  # 展示的频道信息
        self.markline = 0  # 箭头行 初始化设置默认频道
        self.topline = 0  # lines
        self.displayline = 0  # 初始化歌曲信息显示行

        self.display_lines = []  # 需要输出的信息
        self.__cli_title = ''
        self.__cli_love = ''
        self.__cli_prefix_selected = ''
        self.__cli_prefix_deselected = ''
        self.__cli_suffix_selected = ''
        self.__cli_suffix_deselected = ''

        self.screen_height, self.screen_width = self.linesnum()  # 屏幕显示行数

        subprocess.call('echo  "\033[?25l"', shell=True)  # 取消光标

    def set_title(self, string):
        self.__cli_title = string

    def set_love(self, string):
        self.__cli_love = string

    def set_prefix_selected(self, string):
        self.__cli_prefix_selected = string

    def set_prefix_deselected(self, string):
        self.__cli_prefix_deselected = string

    def set_suffix_selected(self, string):
        self.__cli_suffix_selected = string

    def set_suffix_deselected(self, string):
        self.__cli_suffix_deselected = string

    def set_config(self, config):
        """
        设置默认参数
        """
        pass

    def set_displayline(self):
        """
        显示歌曲信息的行号
        """
        self.displayline = self.markline + self.topline

    def linesnum(self):
        """
        测试屏幕显示行数, 每行字符数

        return: 屏幕高度 int
                屏幕宽度 int
        """
        num = subprocess.check_output('stty size', shell=True).split(' ')
        height = int(num[0] - 4)  # -4 上下空余
        width = int(num[1])
        return height, width

    def render(self):
        """
        输出到屏幕
        """
        for line in self.display_lines:
            print line

    def make_display_lines(self):
        """
        生成输出信息
        """
        pass

    def display(self):
        """
        显示信息
        """
        pass

    def run(self):
        """
        监听按键
        """
        while True:
            self.display()
            c = getch.getch()
            if c == 'k':
                self.updown(-1)
            if c == 'j':
                self.updown(1)
            if c == 'q':
                break

    def updown(self, increment):
        """
        屏幕上下滚动

        :params incrment: 1 向下滚动
                          -1 向上滚动
        """
        # paging
        if increment == -1 and self.markline == 0 and self.topline != 0:
            self.topline -= 1
        elif increment == 1 and self.markline + self.topline != len(self.__lines) - 1 and self.markline == self.screen_height:
            self.topline += 1
        # scroll
        if increment == -1 and self.markline != 0:
            self.markline -= 1
        elif increment == 1 and self.markline != self.screen_height and self.markline < len(self.__lines) - 1:
            self.markline += 1

    def is_cn_char(self, i):
        """
        判断是否为中文字符(歌词居中使用)
        """
        return 0x4e00 <= ord(i) < 0x9fa6

    def center_num(self, tmp):
        """
        返回总字符数(考虑英文和中文在终端所占字块)

        return: int
        """
        l = 0
        for i in tmp:
            l += 2 if self.is_cn_char(i) else 1
        return l
