#!/usr/bin/env python2
# -*- coding: utf-8 -*-

class Help(cli.Cli):
    '''帮助界面，查看快捷键'''
    def __init__(self, win):
        self.win = win
        self.win.thread(self.display_help)

    def display_help(self):
        while self.win.state == 2:
            self.display()
            time.sleep(1)

    def __del__(self):
        self.win.state = 0

    def display(self):
        keys = self.win.KEYS
        subprocess.call('clear', shell=True)
        print
        print self.win.TITLE
        print
        print ' '*5 + green('移动') + ' '*17 + green('音乐') + '\r'
        print ' '*5 + '[%(DOWN)s] ---> 下          [space] ---> 播放' % keys + '\r'
        print ' '*5 + '[%(UP)s] ---> 上          [%(OPENURL)s] ---> 打开歌曲主页' % keys + '\r'
        print ' '*5 + '[%(TOP)s] ---> 移到最顶    [%(NEXT)s] ---> 下一首' % keys + '\r'
        print ' '*5 + '[%(BOTTOM)s] ---> 移到最底    [%(RATE)s] ---> 喜欢/取消喜欢' % keys + '\r'
        print ' '*26 + '[%(BYE)s] ---> 不再播放' % keys + '\r'

        print ' '*5 + green('音量') + ' '*17 + '[%(PAUSE)s] ---> 暂停' % keys + '\r'
        print ' '*5 + '[=] ---> 增          [%(QUIT)s] ---> 退出' % keys + '\r'
        print ' '*5 + '[-] ---> 减          [%(LOOP)s] ---> 单曲循环' % keys + '\r'
        print ' '*5 + '[%(MUTE)s] ---> 静音        [e] ---> 播放列表' % keys + '\r'

        print
        print ' '*5 + green('歌词') + '\r'
        print ' '*5 + '[%(LRC)s] ---> 歌词' % keys + '\r'
