#-*- encoding: UTF-8 -*-
'''
用print设计的滚动终端界面

PREFIX_SELECTED:可以指定当前指向行的前缀
PREFIX_DESELECTED:暂时没有用,如果想保持选项行一致需要填写和PREFIX_SELECTED一样大小的空格
SUFFIX_SELECTED:对选中行进行标记
SUFFIX_DESELECTED:暂时无用
TITLE:界面标题的设定
'''
#---------------------------------import------------------------------------
import subprocess
from termcolor import colored
import getch
#---------------------------------------------------------------------------
class Cli(object):
    PREFIX_SELECTED = colored('  > ', 'blue') # 箭头所指行前缀
    PREFIX_DESELECTED = '    '
    SUFFIX_SELECTED = '' # 空格标记行后缀
    SUFFIX_DESELECTED = ''
    TITLE = PREFIX_DESELECTED + colored(' Douban Fm', 'yellow') + ' \ '# 标题

    def __init__(self, lines):
        self.love = colored('♥ ', 'red')
        self.lines = lines
        self.markline = 0 # 箭头行 初始化设置默认频道
        self.topline = 0 # lines
        self.displayline = self.markline # 初始化歌曲信息显示行
        self.screenline = self.linesnum() - 4 # 屏幕显示行数
        subprocess.call('echo  "\033[?25l"', shell=True) # 取消光标

    # 测试屏幕显示行数
    def linesnum(self):
        num = subprocess.check_output('stty size', shell=True)
        return int(num.split(' ')[0])

    # 展示窗口
    def display(self):
        subprocess.call('clear', shell=True) # 清屏
        print
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
            print line + '\r' # 为什么加\r,我不知道,如果不加会出bug

    # 显示歌曲的行号
    def displaysong(self):
        self.displayline = self.markline + self.topline

    # 界面执行程序
    def run(self):
        while True:
            self.display()
            i = getch._Getch()
            c = i()
            if c == 'k':
                self.updown(-1)
            if c == 'j':
                self.updown(1)
            if c == 'q':
                exit()

    # 对上下键进行反应,调成page和scroll
    def updown(self, increment):
        # paging
        if increment == -1 and self.markline == 0 and self.topline != 0:
            self.topline -= 1
        elif increment == 1 and self.markline + self.topline != len(self.lines) - 1 and self.markline == self.screenline:
            self.topline += 1
        # scroll
        if increment == -1 and self.markline != 0:
            self.markline -= 1
        elif increment == 1 and self.markline != self.screenline:
            self.markline += 1

def main():
    lines = [str(i) for i in range(30)]
    c = Cli(lines)
    c.run()

if __name__ == '__main__':
    main()


