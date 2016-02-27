#!/usr/bin/env python
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
from doubanfm import getch
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
    管理view之间的切换
    """

    def __init__(self):
        self.player = MPlayer()
        self.data = data.Data()
        self.quit_quit = False
        self.current_controller = None  # 当前controller

        self.switch_queue = Queue.Queue(0)
        self.key_queue = Queue.Queue(0)  # 按键队列

        self.view_control_map = {
            'main': MainController(self.player, self.data, self.key_queue),
            'lrc': LrcController(self.player, self.data, self.key_queue),
            'help': HelpController(self.player, self.data, self.key_queue),
            'manager': ManagerController(self.player, self.data, self.key_queue),
            'quit': QuitController(self.player, self.data, self.key_queue)
        }

        # 切换线程
        Thread(target=self._watchdog_switch).start()
        Thread(target=self._watchdog_key).start()

    def _watchdog_switch(self):
        """
        切换页面线程
        """
        # init
        self.current_controller = self.view_control_map['main']
        self.current_controller.run(self.switch_queue)

        while not self.quit_quit:
            key = self.switch_queue.get()
            if key == 'quit_quit':
                self.quit_quit = True
            else:
                self.current_controller = self.view_control_map[key]
                self.current_controller.run(self.switch_queue)

        # 退出保存信息
        self.quit()
        os._exit(0)

    def quit(self):
        # 退出保存信息
        self.data.save()
        subprocess.call('echo -e "\033[?25h";clear', shell=True)

    def _watchdog_key(self):
        """
        接受按键, 存入queue
        """
        while True:
            k = getch.getch()
            self.key_queue.put(k)


def main():
    router = Router()

    from flask import Flask, request
    app = Flask(__name__)

    @app.route('/', methods=['POST'])
    def index():
        router.key_queue.put(request.form['ch'])
        return 'OK'

    app.run()


if __name__ == '__main__':
    main()
