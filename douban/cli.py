#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
用print设计的滚动终端界面

PREFIX_SELECTED:可以指定当前指向行的前缀
PREFIX_DESELECTED:暂时没有用,如果想保持选项行一致需要填写和PREFIX_SELECTED一样大小的空格
SUFFIX_SELECTED:对选中行进行标记
SUFFIX_DESELECTED:暂时无用
TITLE:界面标题的设定
'''
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
from colorset.colors import color_func


class Cli(object):
    c = db_config.theme
    PREFIX_SELECTED = color_func(c['LINE']['arrow'])('  > ')  # 箭头所指行前缀
    LOVE = color_func(c['PLAYINGSONG']['like'])(' ❤ ', 'red')
    PREFIX_DESELECTED = '    '
    SUFFIX_SELECTED = ''  # 空格标记行后缀
    SUFFIX_DESELECTED = ''
    TITLE = PREFIX_DESELECTED  # 标题

    def __init__(self, lines):
        self.lines = lines
        self.markline = 0  # 箭头行 初始化设置默认频道
        self.topline = 0  # lines
        self.displayline = self.markline  # 初始化歌曲信息显示行
        self.screen_height, self.screen_width = self.linesnum()  # 屏幕显示行数
        subprocess.call('echo  "\033[?25l"', shell=True)  # 取消光标

    def linesnum(self):
        '''测试屏幕显示行数,每行字符数'''
        num = subprocess.check_output('stty size', shell=True)
        tmp = num.split(' ')
        return int(tmp[0]) - 4, int(tmp[1])  # -4上下空余

    def display(self):
        '''展示窗口'''
        self.screen_height, self.screen_width = self.linesnum()  # 屏幕显示行数
        subprocess.call('clear', shell=True)  # 清屏
        print
        print self.TITLE
        top = self.topline
        bottom = self.topline + self.screen_height + 1
        for index, i in enumerate(self.lines[top:bottom]):
            # 箭头指向
            if index == self.markline:
                prefix = self.PREFIX_SELECTED
                i = color_func(self.c['LINE']['highlight'])(i)
            else:
                prefix = self.PREFIX_DESELECTED
            # 选择频道
            if index + self.topline == self.displayline:
                suffix = self.SUFFIX_SELECTED
            else:
                suffix = self.SUFFIX_DESELECTED
            line = '%s %s %s' % (prefix, i, suffix)
            line = color_func(self.c['LINE']['line'])(line)
            print line + '\r'  # 为什么加\r,我不知道,如果不加会出bug

    def displaysong(self):
        '''显示歌曲的行号'''
        self.displayline = self.markline + self.topline

    def run(self):
        '''界面执行程序'''
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
        '''对上下键进行反应,调成page和scroll'''
        # paging
        if increment == -1 and self.markline == 0 and self.topline != 0:
            self.topline -= 1
        elif increment == 1 and self.markline + self.topline != len(self.lines) - 1 and self.markline == self.screen_height:
            self.topline += 1
        # scroll
        if increment == -1 and self.markline != 0:
            self.markline -= 1
        elif increment == 1 and self.markline != self.screen_height and self.markline < len(self.lines) - 1:
            self.markline += 1

    def is_cn_char(self, i):
        '''判断中文字符'''
        return 0x4e00 <= ord(i) < 0x9fa6

    def center_num(self, tmp):
        ''' 考虑英文和中文在终端上所占字块 '''
        l = 0
        for i in tmp:
            l += 2 if self.is_cn_char(i) else 1
        return l


def main():
    lines = [str(i) for i in range(30)]
    c = Cli(lines)
    c.run()

if __name__ == '__main__':
    main()
