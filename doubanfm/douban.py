#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
豆瓣fm主程序
"""
from threading import Thread
# import notification             # desktop notification
import subprocess
import logging
import Queue
import sys
import os

from doubanfm import data
from doubanfm.player import MPlayer       # player
from doubanfm.controller.main_controller import MainController
from doubanfm.controller.lrc_controller import LrcController
from doubanfm.controller.help_controller import HelpController
from doubanfm.controller.manager_controller import ManagerController
from doubanfm.controller.quit_controller import QuitController

reload(sys)
sys.setdefaultencoding('utf8')

# root logger config
logging.basicConfig(
    format="%(asctime)s - \
[%(process)d]%(filename)s:%(lineno)d - %(levelname)s: %(message)s",
    datefmt='%Y-%m-%d %H:%I:%S',
    filename=os.path.expanduser('~/.doubanfm.log'),
    level=logging.INFO
)

# Set up our own logger
logger = logging.getLogger('doubanfm')
logger.setLevel(logging.INFO)


class Router(object):
    """
    集中管理view之间的切换
    """

    def __init__(self):
        self.player = MPlayer()
        self.data = data.Data()
        self.quit_quit = False

        self.switch_queue = Queue.Queue(0)

        self.view_control_map = {
            'main': MainController(self.player, self.data),
            'lrc': LrcController(self.player, self.data),
            'help': HelpController(self.player, self.data),
            'manager': ManagerController(self.player, self.data),
            'quit': QuitController(self.player, self.data)
        }

        # 切换线程
        Thread(target=self._watchdog_switch).start()

    def _watchdog_switch(self):
        """
        切换页面线程
        """
        # init
        self.view_control_map['main'].run(self.switch_queue)

        while not self.quit_quit:
            key = self.switch_queue.get()
            if key == 'quit_quit':
                self.quit_quit = True
            else:
                self.view_control_map[key].run(self.switch_queue)

        # 退出保存信息
        self.quit()
        os._exit(0)

    def quit(self):
        # 退出保存信息
        self.data.save()
        subprocess.call('echo -e "\033[?25h";clear', shell=True)


def main():
    Router()

if __name__ == '__main__':
    main()
