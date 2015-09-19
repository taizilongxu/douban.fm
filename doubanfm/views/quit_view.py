#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from doubanfm.views.help_view import Help
from doubanfm.dal.dal_quit import QuitDal


class Quit(Help):
    '''退出界面'''
    def __init__(self, data):
        super(Quit, self).__init__(data)

    def set_dal(self):
        dal = QuitDal(self.data)
        self.info = dal.info

    def make_display_lines(self):
        self.screen_height, self.screen_width = self.linesnum()  # 屏幕显示行数
        display_lines = []

        for i in range(self.screen_height):
            if i == self.screen_height / 2:
                display_lines.append(' ' * ((self.screen_width - 18)/2) + self.info)
            else:
                display_lines.append('')

        self.display_lines = display_lines
