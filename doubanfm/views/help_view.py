#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import subprocess

from doubanfm.views.lrc_view import Lrc
from doubanfm.dal.dal_help import HelpDal


class Help(Lrc):
    """帮助界面"""
    def __init__(self, data):
        super(Help, self).__init__(data)

    def set_dal(self):
        dal = HelpDal(self.data)
        self.c = dal.c  # 主题
        self.set_title(dal.title)
        self.set_suffix_selected(dal.suffix_selected)
        self.set_lines(dal.lines)

    def display(self):
        self.set_dal()
        self.make_display_lines()
        subprocess.call('clear', shell=True)
        for i in self.display_lines:
            print i

    def make_display_lines(self):
        self.screen_height, self.screen_width = self.linesnum()  # 屏幕显示行数

        display_lines = ['']
        display_lines.append(self._title + '\r')
        display_lines.append('')

        display_lines += self._lines

        self.display_lines = display_lines
