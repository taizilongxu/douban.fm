#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import logging
from threading import Thread

from doubanfm.views import quit_view
from doubanfm import getch
from doubanfm.controller.lrc_controller import LrcController

logger = logging.getLogger('doubanfm')  # get logger


class QuitController(LrcController):
    """
    按键控制
    """

    def __init__(self, player, data):
        # 接受player, data, view
        super(QuitController, self).__init__(player, data)
        self.view = quit_view.Quit(self.data)

    def _watchdog_queue(self):
        """
        从queue里取出字符执行命令
        """
        k = self.queue.get()
        if k == 'q':  # 退出
            self.player.quit()
            self.switch_queue.put('quit_quit')
        else:
            self.switch_queue.put('main')
        self.quit = True

    def _controller(self):
        """
        接受按键, 存入queue
        """
        k = getch.getch()
        self.queue.put(k)
