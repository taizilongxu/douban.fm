#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import logging
import copy
from threading import Thread

from doubanfm.views import main_view

logger = logging.getLogger('doubanfm')


class MainController(object):
    """
    主界面控制:

    提供run方法以调用该控制
    run方法启动三个线程:
        1. _watchdog_queue: 操作按键对应的命令
        2. _watchdog_time: 标题行需要显示歌曲播放进度

    """

    def __init__(self, player, data, queue):
        # 接受player, data
        self.player = player
        self.data = data
        self.keys = data.keys
        self.playingsong = None
        self.quit = False

        self._bind_view()
        self.player.start_queue(self, data.volume)
        self.queue = queue  # 键盘和http控制队列
        self.rate_times = 0

    def _bind_view(self):
        self.view = main_view.Win(self.data)  # 绑定view

    def run(self, switch_queue):
        """
        每个controller需要提供run方法, 来提供启动
        """
        self.switch_queue = switch_queue
        self.quit = False

        Thread(target=self._watchdog_queue).start()
        Thread(target=self._watchdog_time).start()

    def before_play(self):
        """
        """
        pass

    def after_play(self, playingsong, rate_times):
        """
        """
        if not self.quit:
            # 提交播放完毕
            Thread(target=self.submit_music, args=(playingsong,)).start()
            Thread(target=self.submit_rate, args=(playingsong, rate_times,)).start()

    def submit_music(self, playingsong):
        self.data.submit_music(playingsong)

    def submit_rate(self, playingsong, rate_times):
        if rate_times % 2 == 1:
            if playingsong['like']:
                self.data.set_song_unlike(playingsong)
            else:
                self.data.set_song_like(playingsong)

    def display(info):
        def _deco(func):
            def _func(self, *args, **kwargs):
                if info and self.view and not self.quit:
                    self.view.override_suffix_selected(info)
                    self.view.display()
                    tmp = func(self, *args, **kwargs)
                    self.view.cancel_override()
                else:
                    tmp = func(self, *args, **kwargs)
                return tmp
            return _func
        return _deco

    # 提供给player的两个方法
    def get_playingsong(self):
        self.playingsong = self.data.playingsong
        return self.playingsong

    @display('正在加载歌曲...')
    def get_song(self):
        """
        切换歌曲时刷新
        """
        if self.playingsong:
            playingsong = copy.deepcopy(self.playingsong)
            rate_times = self.rate_times
            logger.info(playingsong['title'])
            self.after_play(playingsong, rate_times)
        self.playingsong = self.data.get_song()
        self.rate_times = 0
        return self.playingsong

    def up(self):
        self.view.up()
        self.view.display()

    def down(self):
        self.view.down()
        self.view.display()

    def go_bottom(self):
        self.view.go_bottom()
        self.view.display()

    def go_top(self):
        self.view.go_top()
        self.view.display()

    @display('切换频道中...')
    def set_channel(self):
        self.data.channel = self.view.set_channel()  # 获取view里的channel索引
        self.data.set_channel(self.data.channel)  # 设置API里的channel
        self.player.next()

    def set_mute(self):
        if self.data.mute:
            self.data.volume = self.data.mute
            self.data.mute = False
            self.player.set_volume(self.data.volume)
        else:
            self.data.mute = self.data.volume
            self.data.volume = 0
            self.player.set_volume(0)
        self.view.display()

    def set_loop(self):
        self.data.loop = False if self.data.loop else True
        self.player.loop()
        self.view.display()

    def set_rate(self):
        self.data.song_like = False if self.data.song_like else True
        self.rate_times += 1  # 最后提交计算
        self.view.display()

    def set_pause(self):
        self.data.pause = False if self.data.pause else True
        self.player.pause()
        self.view.display()

    def set_volume(self, vol):
        self.data.change_volume(vol)
        self.player.set_volume(self.data.volume)
        self.view.display()

    def set_high(self):
        self.data.netease = False if self.data.netease else True
        self.view.display()

    def set_theme(self, k):
        self.data.set_theme_id(int(k) - 1)
        self.view.display()

    @display('获取歌词中...')
    def set_lrc(self):
        self.switch_queue.put('lrc')

    @display('等待播放器装填...')
    def set_next(self):
        self.player.next()

    @display('不再播放...')
    def set_bye(self):
        Thread(target=self.data.bye).start()
        # self.player.start_queue(self)
        self.player.next()

    @display('已在浏览器打开专辑主页')
    def set_url(self):
        '''打开豆瓣网页'''
        import webbrowser
        url = "http://music.douban.com" + \
            self.data.playingsong['album'].replace('\/', '/')
        webbrowser.open(url)

    def _watchdog_time(self):
        """
        标题时间显示
        """
        while not self.quit:
            import time
            self.data.time = self.player.time_pos
            self.view.display()
            time.sleep(1)

    def _watchdog_queue(self):
        """
        从queue里取出字符执行命令
        """

        while not self.quit:
            k = self.queue.get()
            if k == self.keys['QUIT']:  # 退出
                self.quit = True
                self.switch_queue.put('quit')
            elif k == self.keys['BYE']:
                self.set_bye()
            elif k == ' ':  # 播放该频道
                self.set_channel()
                self.player.start_queue(self)
            elif k == self.keys['LOOP']:  # 单曲循环
                self.set_loop()
            elif k == self.keys['RATE']:  # 加心/去心
                self.set_rate()

            elif k == self.keys['OPENURL']:  # 打开当前歌曲豆瓣专辑
                self.set_url()

            elif k == self.keys['LRC']:  # 歌词
                self.set_lrc()
                self.quit = True
            elif k == self.keys['HELP']:
                self.quit = True
                self.switch_queue.put('help')
            elif k == self.keys['HIGH']:  # 高品质音乐
                self.set_high()
            elif k == 't':  # 管理界面
                self.quit = True
                self.switch_queue.put('manager')

            # getch will return multiple ASCII codes for arrow keys
            # A, B, C, D are the first code of UP, DOWN, LEFT, RIGHT
            elif k == self.keys['UP'] or k == 'B':  # 向下
                self.up()
            elif k == self.keys['DOWN'] or k == 'A':  # 向上
                self.down()
            elif k == self.keys['BOTTOM']:
                self.go_bottom()
            elif k == self.keys['TOP']:
                self.go_top()

            elif k == self.keys['PAUSE']:  # 暂停
                self.set_pause()
            elif k == self.keys['NEXT']:  # 下一首
                self.set_next()

            elif k == '-' or k == '_':  # 减小音量
                self.set_volume(-1)
            elif k == '+' or k == '=':  # 增大音量
                self.set_volume(1)
            elif k == self.keys['MUTE']:  # 静音
                self.set_mute()

            elif k in ['1', '2', '3', '4']:  # 主题选取
                self.set_theme(k)
