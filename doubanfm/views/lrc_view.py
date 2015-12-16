#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import logging
from main_view import Win
from threading import RLock

from doubanfm.colorset.colors import color_func  # colors
from doubanfm.dal.dal_lrc import LrcDal

logger = logging.getLogger('doubanfm')
mutex = RLock()


class Lrc(Win):
    """歌词显示界面"""

    def __init__(self, data):
        super(Lrc, self).__init__(data)
        self.lrc_offset = 0

    def set_dal(self):
        dal = LrcDal(self.data, self.lrc_offset)
        self.c = dal.c  # 主题
        self.set_title(dal.title)
        self.set_suffix_selected(dal.suffix_selected)
        self.set_lines(dal.lines)
        self.set_sort_lrc_dict(dal.sort_lrc_dict)

    def display(self):
        mutex.acquire()
        try:
            self.set_dal()
            self.markline = self.find_line()
            self.make_display_lines()
            # logger.info(self.display_lines)
            print '\n'.join(self.display_lines)
            # for i in self.display_lines:
            #     print i
        finally:
            mutex.release()

    def find_line(self):
        """第一次载入时查找歌词"""
        for now_time in reversed(range(self.data.time)):
            locate = [index for index, i in enumerate(self._sort_lrc_dict)
                      if i[0] == now_time]  # 查找歌词在self.sort_lrc_dict中的位置
            if locate:
                return locate[0] + self.lrc_offset
        return 0

    def make_display_lines(self):
        """通过歌词生成屏幕需要显示的内容"""
        self.screen_height, self.screen_width = self.linesnum()  # 屏幕显示行数

        display_lines = ['']
        display_lines.append(self._title + '\r')
        display_lines.append('')

        scroll_line_num = self.screen_height - 6
        for linenum in range(scroll_line_num):
            if scroll_line_num/2 - linenum > self.markline - self.topline or \
                    linenum - scroll_line_num/2 >= len(self._lines) - self.markline:
                display_lines.append('\r')
            else:
                line = self._lines[self.markline - (scroll_line_num/2 - linenum)]
                line = line.strip('\n')
                l = self.center_num(line)
                flag_num = (self.screen_width - l) / 2
                if linenum == scroll_line_num/2:
                    i = color_func(self.c['LRC']['highlight'])(line)
                    display_lines.append(' ' * flag_num + i + '\r')
                else:
                    line = color_func(self.c['LRC']['line'])(line)
                    display_lines.append(' ' * flag_num + line + '\r')

        display_lines.append('')  # 空行
        display_lines.append(self.center_suffix_selected() + '\r')  # 歌词页面标题

        self.display_lines = display_lines

    def center_suffix_selected(self):
        # 歌曲信息居中
        song = self.data.playingsong
        tmp = (
            song['title'] +
            song['albumtitle'] +
            song['artist']
        ).replace('\\', '').strip()
        l = self.center_num(tmp)
        l += 2 if song['like'] else 0
        flag_num = (self.screen_width - l - 6) / 2
        return ' ' * flag_num + self._suffix_selected + '\r'  # 歌词页面标题

    def up(self):
        self.lrc_offset -= 1
        self.display()

    def down(self):
        self.lrc_offset += 1
        self.display()
