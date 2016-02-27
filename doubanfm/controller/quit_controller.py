#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import logging

from doubanfm.views import quit_view
from doubanfm.controller.lrc_controller import LrcController

logger = logging.getLogger('doubanfm')  # get logger


class QuitController(LrcController):
    """
    按键控制
    """

    def __init__(self, player, data, queue):
        # 接受player, data, view
        super(QuitController, self).__init__(player, data, queue)

    def _bind_view(self):
        self.view = quit_view.Quit(self.data)

    def _watchdog_queue(self):
        """
        从queue里取出字符执行命令
        """
        k = self.queue.get()
        if k == self.keys['QUIT']:  # 退出
            self.player.quit()
            self.switch_queue.put('quit_quit')
        else:
            self.switch_queue.put('main')
        self.quit = True
