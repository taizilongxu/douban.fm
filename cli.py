#-*- encoding: UTF-8 -*-
#---------------------------------import------------------------------------
import subprocess
import time
from termcolor import colored
import getch
#---------------------------------------------------------------------------
lines = [str(i) for i in range(30)]

class Cli(object):
    PREFIX_SELECTED = colored('  > ', 'blue') # 箭头所指行前缀
    PREFIX_DESELECTED = '    '
    SUFFIX_SELECTED = '' # 空格标记行后缀
    SUFFIX_DESELECTED = ''
    VERSION = ' v0.1.0 '
    TITLE = PREFIX_DESELECTED + colored(' Douban Fm', 'yellow') + VERSION + ' \ '# 标题

    def __init__(self, lines):
        self.love = colored('♥ ', 'red')
        self.lines = lines
        self.markline = 0 # 箭头行
        self.topline = 0 # lines
        self.displayline = -1 # 歌曲信息
        self.screenline = 15

        self.run()

    def display(self):
        subprocess.call('clear;echo  "\033[?25l"', shell=True) # 取消光标
        print self.TITLE
        top = self.topline
        bottom = self.topline + self.screenline + 1
        for index,i in enumerate(self.lines[top:bottom]):
            '箭头指向'
            if index == self.markline:
                prefix = self.PREFIX_SELECTED
                i = colored(i, 'blue')
            else:
                prefix = self.PREFIX_DESELECTED
            '选择频道'
            if index + self.topline == self.displayline:
                suffix = self.SUFFIX_SELECTED
            else:
                suffix = self.SUFFIX_DESELECTED
            line = '%s %s %s' % (prefix, i, suffix)
            print line

    def displaysong(self):
        self.displayline = self.markline + self.topline

    def run(self):
        while True:
            self.display()
            i = getch._Getch()
            c = i()
            if c == 'k':
                self.updown(-1)
            if c == 'j':
                self.updown(1)
            if c == ' ':
                self.displaysong()
            if c == 'q':
                exit()

    def updown(self, increment):
        # paging
        if increment == -1 and self.markline == 0 and self.topline != 0:
            self.topline -= 1
        elif increment == 1 and self.markline + self.topline != len(self.lines) - 1and self.markline == self.screenline:
            self.topline += 1
        # scroll
        if increment == -1 and self.markline != 0:
            self.markline -= 1
        elif increment == 1 and self.markline != self.screenline:
            self.markline += 1
def main():
    c = Cli(lines)

if __name__ == '__main__':
    main()


