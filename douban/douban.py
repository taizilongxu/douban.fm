#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
豆瓣fm主程序
"""
# local
from player import MPlayer       # player
# import notification             # desktop notification
# from config import db_config    # config
# from colorset.colors import on_light_red, color_func  # colors
import Queue
import logging
import os
from threading import Thread
from model import Playlist, Channel
from config import db_config

from controller.main_controller import MainController
from controller.lrc_controller import LrcController

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


class Data(object):
    """
    所有需要的数据统一在一起
    """

    def __init__(self):
        self.playlist = Playlist()
        self.lines = Channel().lines
        # self.hitory = History()
        self.key = db_config.keys
        self.vol = db_config.volume
        self.theme = db_config.theme
        self.channel = db_config.channel
        self.user_name = db_config.user_name
        self.loop = False
        self.pro = False
        self.time = 0

    @property
    def lrc(self):
        return self.playlist.get_lrc()

    @property
    def playingsong(self):
        return self.playlist.get_playingsong()

class Router(object):
    """
    集中管理view之间的切换
    """

    def __init__(self):
        self.player = MPlayer()
        self.data = Data()

        self.switch_queue = Queue.Queue(0)

        self.view_control_map = {
            'main': MainController(self.player, self.data),
            'lrc': LrcController(self.player, self.data),
            'quit': False
        }

        # init
        self.view_control_map['main'].run(self.switch_queue)

        # 切换线程
        Thread(target=self._watchdog_switch).start()

    def _watchdog_switch(self):
        while not self.view_control_map['quit']:
            key = self.switch_queue.get()
            if key == 'quit':
                self.view_control_map['quit'] = True
            else:
                self.view_control_map[key].run(self.switch_queue)


Router()


# import time
# time.sleep(10)

# data_main_view = MainDal(playlist.get_playingsong(), mutex_play_state, config)

# print data_main_view.title
# print data_main_view.suffix_selected



# def watchdog(self):
#     '''守护线程，检查歌曲是否播放完毕'''
#     while not self.q:
#         if not self.player.is_alive:
#             # Reduce some CPU use (useful when player not yet started)
#             time.sleep(1)
#         logger.debug('Wait till player exit.')
#         self._player_exit_event.wait()      # Wait for event
#         self._player_exit_event.clear()     # Clear the event
#         logger.debug('Noticed player exit.')
#         # If self.q (about to quit), just quit
#         if self.q:
#             return
#         self.thread(self.douban.submit_music, args=(self.playingsong,))
#         # If some thread has already called play(), just pass
#         if not self.lock_start:
#             self.play()

# def run(self):
#     while True:
#         k = getch.getch()
#         if k == KEYS['UP']:
#             pass
#         elif k == KEYS['DOWN']:
#             pass
#         elif k == ' ':
#             pass
#         elif k == KEYS['BYE']:
#             pass
#         elif k == KEYS['NEXT']:
#             pass


# def run(self):
#     '''主交互逻辑 (key event loop)'''
#     while True:
#         self.display()
#         k = getch.getch()
#         if self.state != 1:  # 歌词模式下除了方向键都可以用
#             # getch will return multiple ASCII codes for arrow keys
#             # A, B, C, D are the first code of UP, DOWN, LEFT, RIGHT
#             if k == self.KEYS['UP'] or k == 'A':
#                 self.updown(-1)
#             elif k == self.KEYS['DOWN'] or k == 'B':
#                 self.updown(1)
#             elif k == self.KEYS['TOP']:      # g键返回顶部
#                 self.markline = 0
#                 self.topline = 0
#             elif k == self.KEYS['BOTTOM']:   # G键返回底部
#                 self.markline = self.screen_height
#                 self.topline = len(self.lines) - self.screen_height - 1
#         if k == self.KEYS['HELP']:     # help界面
#             self.state = 2
#             Help(self)
#         elif k == self.KEYS['LRC']:      # o歌词
#             self.set_lrc()
#             self.state = 1
#             self.thread(self.display_lrc)
#         elif k == 'e' and self.state == 0:
#             self.state = 3
#             History(self)
#         elif k == self.KEYS['RATE']:     # r标记红心/取消标记
#             self.thread(self.set_rate)
#         elif k == self.KEYS['NEXT']:     # n下一首
#             self.set_next()
#         elif k == ' ':                   # 空格选择频道,播放歌曲
#             if self.markline + self.topline != self.displayline:
#                 self.displaysong()
#                 self.set_channel()
#         elif k == self.KEYS['OPENURL']:  # l打开当前播放歌曲豆瓣页
#             self.set_url()
#         elif k == self.KEYS['BYE']:      # b不再播放
#             self.set_bye()
#         elif k == self.KEYS['PAUSE']:    # p暂停
#             self.pause()
#         elif k == self.KEYS['MUTE']:     # m静音
#             self.mute()
#         elif k == self.KEYS['LOOP']:     # l单曲循环
#             self.set_loop()
#         elif k == self.KEYS['QUIT']:     # q退出程序
#             if self.state == 0:
#                 self.state = 4
#                 Quit(self)
#             else:
#                 self.state = 0
#                 self.display()
#         elif k == '=' or k == '+':       # 提高音量
#             self.change_volume(1)
#         elif k == '-' or k == '_':       # 降低音量
#             self.change_volume(-1)
#         elif k in ['1', '2', '3', '4']:
#             db_config.theme = int(k) - 1
#             self.reload_theme()






#     def info(args):
#         '''装饰器，用来改变SUFFIX_SELECTED并在界面输出'''
#         def _deco(func):
#             def _func(self):
#                 tmp = self.SUFFIX_SELECTED
#                 self.SUFFIX_SELECTED = args
#                 self.display()
#                 self.SUFFIX_SELECTED = tmp
#                 func(self)
#             return _func
#         return _deco

#     def set_rate(self):
#         '''歌曲加心，去心'''
#         while self.lock_rate:
#             if self.q:
#                 return
#         self.lock_rate = True
#         if self.playingsong:
#             if not self.playingsong['like']:
#                 self.SUFFIX_SELECTED = self.LOVE + self.SUFFIX_SELECTED
#                 self.display()
#                 self.douban.rate_music(self.playingsong)
#                 self.playingsong['like'] = 1
#                 self.noti.send_notify(self.playingsong, '标记红心')
#             else:
#                 self.SUFFIX_SELECTED = self.SUFFIX_SELECTED[len(self.LOVE):]
#                 self.display()
#                 self.douban.unrate_music(self.playingsong)
#                 self.playingsong['like'] = 0
#                 self.noti.send_notify(self.playingsong, '取消标记红心')
#         self.lock_rate = False

#     def set_loop(self):
#         '''设置单曲循环'''
#         if self.lock_loop:
#             self.noti.send_notify(self.playingsong, '停止单曲循环')
#             self.lock_loop = False
#         else:
#             self.noti.send_notify(self.playingsong, '单曲循环')
#             self.lock_loop = True

#     def set_url(self):
#         '''打开豆瓣网页'''
#         import webbrowser
#         url = "http://music.douban.com" + \
#             self.playingsong['album'].replace('\/', '/')
#         webbrowser.open(url)

#     def set_quit(self):
#         '''退出播放'''
#         self.q = True
#         self.player.quit()
#         subprocess.call('echo -e "\033[?25h";clear', shell=True)
#         logger.debug('Terminal reset.')
#         # store the token and the default info
#         self.douban.login_data.update({'volume': self._volume,
#                                        'channel': self._channel})
#         logger.info(self.douban.login_data)
#         db_config.save_config(self.history, self.douban.login_data)
#         sys.exit(0)

#     @info('正在加载请稍后...')
#     def set_channel(self):
#         '''开始播放'''
#         if self._channel == self.displayline:
#             return
#         self._channel = self.displayline
#         self.douban.set_channel(self._channel)  # 对douban的post_data修改频道
#         self.get_playlist()
#         self.lock_loop = False
#         self.lock_start = True
#         self.player.quit()
#         self.play()

#     @info('正在加载请稍后...')
#     def set_next(self):
#         '''开始下一曲'''
#         if self.player.is_alive:
#             self.lock_loop = False
#             self.lock_start = True
#             self.player.quit()
#             if self.state != 3:
#                 self.playlist = self.douban.skip_song(self.playingsong)
#             self.play()

#     @info('不再播放，切换下一首...')
#     def set_bye(self):
#         '''不再播放并进入下一曲'''
#         if self.playingsong:
#             self.lock_start = True  # 每个play前需self.start置0
#             self.player.quit()
#             self.playlist = self.douban.bye(self.playingsong)
#             self.play()

#     @info('正在查找歌词...')
#     def set_lrc(self):
#         '''显示歌词'''
#         self.state = 1
#     def reload_theme(self):
#         # 箭头所指行前缀
#         Cli.c = db_config.theme
#         Cli.PREFIX_SELECTED = color_func(self.c['LINE']['arrow'])('  > ')
#         Cli.LOVE = color_func(self.c['PLAYINGSONG']['like'])(' ❤ ', 'red')

#         self.TITLE = Cli.TITLE + color_func(self.c['TITLE']['doubanfm'])(' Douban Fm ')

#         self.TITLE += '\ ' + \
#             color_func(self.c['TITLE']['username'])(self.douban.login_data['user_name']) + \
#             ' >>'
#         self.set_suffix_selected(self.playingsong)


#     def play(self):
#         '''播放歌曲'''
#         self.lock_start = True
#         self.find_lrc = False
#         self.lrc_dict = {}  # 歌词清空
#         self.songtime = 0  # 重置歌曲时间
#         self.playingsong = self.get_song()
#         if not self.lock_loop:
#             self.playingsong['time'] = time.strftime("%Y-%m-%d %H:%M:%S",
#                                                      time.localtime())
#             self.history.insert(0, self.playingsong)
#         song = self.playingsong

#         self.thread(self.noti.send_notify, args=(self.playingsong,))  # 桌面通知

#         self.set_suffix_selected(song)

#         logger.debug("Start playing %s - %s.", song['artist'], song['title'])
#         self.player.start(song['url'].replace('\\', ''))

#         self.lock_pause = False

#         if self.state == 1:  # 获取歌词
#             self.thread(self.display_lrc)
#         self.lock_start = False

#     def pause(self):
#         '''暂停歌曲'''
#         if self.lock_pause:
#             self.lock_pause = False
#             self.noti.send_notify(self.playingsong, '开始播放')
#         else:
#             self.noti.send_notify(self.playingsong, '暂停播放')
#             self.lock_pause = True
#         self.player.pause()
#     def change_volume(self, increment):
#         '''调整音量大小'''
#         if increment == 1:
#             self._volume += 5
#         else:
#             self._volume -= 5
#         self._volume = max(min(self._volume, 100), 0)  # 限制在0-100之间
#         self.lock_muted = False if self._volume else True
#         self.player.set_volume(self._volume)

#     def mute(self):
#         '''静音'''
#         if self.lock_muted:
#             self.lock_muted = False
#             if self._volume == 0:
#                 self._volume = 10
#             volume = self._volume
#         else:
#             self.lock_muted = True
#             volume = 0
#         self.player.set_volume(volume)

#     def display_time(self):
#         '''时间/音量显示线程'''
#         length = len(self.TITLE)
#         rest_time = 0
#         while not self.q:
#             if self.lock_pause or self.lock_start:
#                 time.sleep(1)
#                 continue
#             if self.player.is_alive:
#                 songtime = self.player.time_pos
#                 if songtime:
#                     self.songtime = songtime
#                 # 181s -> 03:01
#                 rest_time = int(self.playingsong['length']) - self.songtime - 1
#                 minute = int(rest_time) / 60
#                 sec = int(rest_time) % 60
#                 show_time = str(minute).zfill(2) + ':' + str(sec).zfill(2)

#                 title_pro = '' if self.playingsong['kbps'] == '64' else self.PRO
#                 title_kbps = self.playingsong['kbps'] + 'kbps'
#                 title_time = show_time
#                 title_rate = self.RATE[int(round(self.playingsong['rating_avg'])) - 1]
#                 title_vol = '✖' if self.lock_muted else str(self._volume) + '%'
#                 title_loop = '↺' if self.lock_loop else '→'
#                 title = [
#                     color_func(self.c['TITLE']['pro'])(title_pro),
#                     color_func(self.c['TITLE']['kbps'])(title_kbps),
#                     color_func(self.c['TITLE']['time'])(title_time),
#                     color_func(self.c['TITLE']['rate'])(title_rate),
#                     color_func(self.c['TITLE']['vol'])(title_vol),
#                     color_func(self.c['TITLE']['state'])(title_loop)
#                 ]
#                 self.TITLE = \
#                     self.TITLE[:length - 1] + ' ' + ' '.join(title) + '\r'
#             else:
#                 self.TITLE = self.TITLE[:length]
#             self.display()
#             time.sleep(1)


#     def thread(self, target, args=()):
#         '''启动新线程'''
#         threading.Thread(target=target, args=args).start()

#     def display_lrc(self):
#         '''歌词显示线程'''
#         # TODO
#         if not self.find_lrc:
#             self.find_lrc = True
#             self.lrc_dict = self.douban.get_lrc(self.playingsong)
#         if self.lrc_dict:
#             Lrc(self.lrc_dict, self)
#         else:
#             self.state = 0




# def main():
#     Win(douban)

# if __name__ == '__main__':
#     main()
