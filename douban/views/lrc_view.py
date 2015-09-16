#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from main_view import Win
import subprocess
from colorset.colors import color_func  # colors
from dal.dal_lrc import LrcDal


class Lrc(Win):
    """歌词显示界面"""

    def __init__(self, data):
        super(Lrc, self).__init__(data)

    def set_dal(self):
        dal = LrcDal(self.data)
        self.c = dal.c  # 主题
        self.set_title(dal.title)
        self.set_suffix_selected(dal.suffix_selected)
        self.set_lines(dal.lines)
        self.set_sort_lrc_dict(dal.sort_lrc_dict)

    def display(self):
        self.set_dal()
        self.markline = self.find_line()
        self.make_display_lines()
        for i in self.display_lines:
            print i

    def find_line(self):
        """第一次载入时查找歌词"""
        for now_time in reversed(range(self.data.time)):
            locate = [index for index, i in enumerate(self._sort_lrc_dict)
                      if i[0] == now_time]  # 查找歌词在self.sort_lrc_dict中的位置
            if locate:
                return locate[0]
        return 0

    # def display_line(self):
    #     """显示歌词当前播放对应行"""
    #     locate = \
    #         [index for index, i in enumerate(self.sort_lrc_dict)
    #             if i[0] == self.song_time]
    #     if locate:
    #         self.markline = locate[0]

    def make_display_lines(self):
        """通过歌词生成屏幕需要显示的内容"""
        self.screen_height, self.screen_width = self.linesnum()  # 屏幕显示行数

        display_lines = ['\n']
        display_lines.append(self._title + '\r')
        display_lines.append('\n')

        for linenum in range(self.screen_height - 2):
            if self.screen_height/2 - linenum > self.markline - self.topline or \
                    linenum - self.screen_height/2 >= len(self._lines) - self.markline:
                display_lines.append('\r')
            else:
                line = self._lines[self.markline - (self.screen_height/2 - linenum)]
                line = line.strip('\n')
                l = self.center_num(line)
                flag_num = (self.screen_width - l) / 2
                if linenum == self.screen_height/2:
                    i = color_func(self.c['LRC']['highlight'])(line)
                    display_lines.append(' ' * flag_num + i + '\r')
                else:
                    line = color_func(self.c['LRC']['line'])(line)
                    display_lines.append(' ' * flag_num + line + '\r')

        display_lines.append(self.center_suffix_selected())  # 歌词页面标题

        self.display_lines = display_lines

    def center_suffix_selected(self):
        # 歌曲信息居中
        song = self.data.playingsong
        tmp = (
            song['title'] +
            song['albumtitle'] +
            song['artist']
            # song['public_time']
        ).replace('\\', '').strip()
        l = self.center_num(tmp)
        if song['like']:
            l += 2
        flag_num = (self.screen_width - l) / 2
        return ' ' * flag_num + self._suffix_selected + '\r'  # 歌词页面标题
