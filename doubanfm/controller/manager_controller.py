#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
暂时没用
"""
import logging
from threading import Thread

from doubanfm.views import manager_view

logger = logging.getLogger('doubanfm')  # get logger


class ManagerController(object):
    """
    按键控制
    """

    def __init__(self, player, data, queue):
        # 接受player, data, view
        self.player = player
        self.data = data
        self._bind_view()
        self.queue = queue

    def _bind_view(self):
        self.view = manager_view.Manager(self.data)

    def run(self, switch_queue):
        """
        每个controller需要提供run方法, 来提供启动
        """
        self.switch_queue = switch_queue
        self.quit = False

        Thread(target=self._watchdog_queue).start()
        Thread(target=self._watchdog_time).start()

    def _watchdog_time(self):
        """
        标题时间显示
        """
        while not self.quit:
            self.data.time = self.player.time_pos
            self.view.display()
            time.sleep(1)

    def _watchdog_queue(self):
        """
        从queue里取出字符执行命令
        """
        while not self.quit:
            k = self.queue.get()
            if k == 'q':  # 退出
                self.quit = True
                self.switch_queue.put('main')
