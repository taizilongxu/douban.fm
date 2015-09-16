#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from dal_main import MainDal
from colorset.colors import color_func  # colors


class HelpDal(MainDal):

    def __init__(self, data):
        super(HelpDal, self).__init__(data)
        self.keys = data.keys

    @property
    def lines(self):

        keys = self.keys
        lines = []

        lines.append(' '*5 + color_func(self.c['PLAYINGSONG']['title'])('移动') + ' '*17 + color_func(self.c['PLAYINGSONG']['title'])('音乐') + '\r')
        lines.append(' '*5 + '[%(DOWN)s] ---> 下          [space] ---> 播放' % keys + '\r')
        lines.append(' '*5 + '[%(UP)s] ---> 上          [%(OPENURL)s] ---> 打开歌曲主页' % keys + '\r')
        lines.append(' '*5 + '[%(TOP)s] ---> 移到最顶    [%(NEXT)s] ---> 下一首' % keys + '\r')
        lines.append(' '*5 + '[%(BOTTOM)s] ---> 移到最底    [%(RATE)s] ---> 喜欢/取消喜欢' % keys + '\r')
        lines.append(' '*26 + '[%(BYE)s] ---> 不再播放' % keys + '\r')

        lines.append(' '*5 + color_func(self.c['PLAYINGSONG']['title'])('音量') + ' '*17 + '[%(PAUSE)s] ---> 暂停' % keys + '\r')
        lines.append(' '*5 + '[=] ---> 增          [%(QUIT)s] ---> 退出' % keys + '\r')
        lines.append(' '*5 + '[-] ---> 减          [%(LOOP)s] ---> 单曲循环' % keys + '\r')
        lines.append(' '*5 + '[%(MUTE)s] ---> 静音        [e] ---> 播放列表' % keys + '\r')

        lines.append('')
        lines.append(' '*5 + color_func(self.c['PLAYINGSONG']['title'])('歌词') + '\r')
        lines.append(' '*5 + '[%(LRC)s] ---> 歌词' % keys + '\r')

        return lines

