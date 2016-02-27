#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import logging

from doubanfm.views import lrc_view
from doubanfm.controller.main_controller import MainController

logger = logging.getLogger('doubanfm')  # get logger


class LrcController(MainController):
    """
    按键控制
    """

    def __init__(self, player, data, queue):
        # 接受player, data, view
        self.player = player
        self.data = data
        self.keys = data.keys
        self.quit = False
        self.rate_times = 0
        self.queue = queue
        self._bind_view()

    def _bind_view(self):
        self.view = lrc_view.Lrc(self.data)

    def _watchdog_queue(self):
        """
        从queue里取出字符执行命令
        """
        while not self.quit:
            k = self.queue.get()
            if k == self.keys['QUIT']:  # 退出
                self.quit = True
                self.switch_queue.put('main')
            elif k == self.keys['BYE']:
                self.data.bye()
                self.player.start_queue(self)
            elif k == self.keys['LOOP']:  # 单曲循环
                self.set_loop()
            elif k == self.keys['RATE']:  # 加心/去心
                self.set_rate()
            elif k == self.keys['OPENURL']:  # 打开当前歌曲豆瓣专辑
                self.set_url()
            elif k == self.keys['HIGH']:  # 高品质音乐
                self.set_high()
            elif k == self.keys['PAUSE']:  # 暂停
                self.set_pause()
            elif k == self.keys['NEXT']:  # 下一首
                self.player.next()
            elif k == '-' or k == '_':  # 减小音量
                self.set_volume(-1)
            elif k == '+' or k == '=':  # 增大音量
                self.set_volume(1)
            elif k == self.keys['MUTE']:  # 静音
                self.set_mute()
            elif k in ['1', '2', '3', '4']:  # 主题选取
                self.set_theme(k)
            elif k == self.keys['UP'] or k == 'B':  # 向下
                self.up()
            elif k == self.keys['DOWN'] or k == 'A':  # 向上
                self.down()
