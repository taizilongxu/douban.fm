#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from base_view import Cli
import os
from colorset.colors \
    import red, green, on_cyan, on_light_red, color_func  # colors


class Win(Cli):
    '''窗体及播放控制'''
    RATE = ['★'*i for i in range(1, 6)]  # 歌曲评分
    PRO = on_light_red(' PRO ')

    def __init__(self, douban):
        # 线程锁
        self.lock_start = False  # 播放锁,play之前需要加
        self.lock_rate = False   # 加心锁
        self.lock_loop = False   # 循环锁
        self.lock_muted = False  # 静音锁
        self.lock_pause = True   # 暂停锁
        self.q = False           # 退出
        self.songtime = 0        # 歌曲时间
        self.playingsong = None  # 当前播放歌曲

        # state  0    1   2    3       4
        #        main lrc help history quit
        self.state = 0

        self.history = db_config.history

        self.douban = douban

        # default volume
        self._volume = douban.login_data['volume']

        # player controler
        self._player_exit_event = threading.Event()
        self.player = player.MPlayer(self._player_exit_event, self._volume)

        # 快捷键配置
        self.KEYS = db_config.keys

        # 桌面通知
        self.noti = notification.Notify()

        # 存储歌曲信息
        self.lines = self.douban.channels
        self._channel = self.douban.login_data['channel']
        self.playingsong = None
        self.playlist = None
        self.find_lrc = False
        self.lrc_dict = {}  # 歌词

        super(Win, self).__init__(self.lines)

        self.TITLE += color_func(self.c['TITLE']['doubanfm'])(' Douban Fm ')

        self.TITLE += '\ ' + \
            color_func(self.c['TITLE']['username'])(self.douban.login_data['user_name']) + \
            ' >>\r'

        # 启动自动播放
        self.markline = self.displayline = self._channel
        self.lock_start = True
        self.SUFFIX_SELECTED = '正在加载请稍后...'
        self.display()

        self.thread(self.play)          # 播放控制
        self.thread(self.watchdog)      # 播放器守护线程
        self.thread(self.display_time)  # 时间显示
        self.run()

    def make_display_lines(self):
        """
        生成输出行
        """
        self.screen_height, self.screen_width = self.linesnum()  # 屏幕显示行数
        subprocess.call('clear', shell=True)  # 清屏

        display_lines = ['\n']
        display_lines.append(self.TITLE)

        top = self.topline
        bottom = self.topline + self.screen_height + 1

        for index, i in enumerate(self.__lines[top:bottom]):
            # 箭头指向
            if index == self.markline:
                prefix = self.__cli_prefix_selected
                i = color_func(self.c['LINE']['highlight'])(i)
            else:
                prefix = self.__cli_prefix_deselected
            # 选择频道
            if index + self.topline == self.displayline:
                suffix = self.__cli_suffix_selected
            else:
                suffix = self.__cli_suffix_deselected
            line = '%s %s %s' % (prefix, i, suffix)
            line = color_func(self.c['LINE']['line'])(line)

            display_lines.append(line + '\r')  # 为什么加\r,我不知道,如果不加会出bug
        self.display_lines = display_lines

    def set_suffix_selected(self, song):
        if song['like'] == 1:

            love = self.LOVE
        else:
            love = ''
        title = color_func(self.c['PLAYINGSONG']['title'])(song['title'])
        albumtitle = color_func(self.c['PLAYINGSONG']['albumtitle'])(song['albumtitle'])
        artist = color_func(self.c['PLAYINGSONG']['artist'])(song['artist'])
        public_time = color_func(self.c['PLAYINGSONG']['publictime'])(song['public_time']) or ''
        self.SUFFIX_SELECTED = (
            love +
            title + ' • ' +
            albumtitle + ' • ' +
            artist + ' ' +
            public_time
        ).replace('\\', '')

    def display(self):
        '''显示主控制界面'''
        if self.state == 0 and not self.lock_start:
            Cli.display(self)

    def info(args):
        '''装饰器，用来改变SUFFIX_SELECTED并在界面输出'''
        def _deco(func):
            def _func(self):
                tmp = self.SUFFIX_SELECTED
                self.SUFFIX_SELECTED = args
                self.display()
                self.SUFFIX_SELECTED = tmp
                func(self)
            return _func
        return _deco

    def set_rate(self):
        '''歌曲加心，去心'''
        while self.lock_rate:
            if self.q:
                return
        self.lock_rate = True
        if self.playingsong:
            if not self.playingsong['like']:
                self.SUFFIX_SELECTED = self.LOVE + self.SUFFIX_SELECTED
                self.display()
                self.douban.rate_music(self.playingsong)
                self.playingsong['like'] = 1
                self.noti.send_notify(self.playingsong, '标记红心')
            else:
                self.SUFFIX_SELECTED = self.SUFFIX_SELECTED[len(self.LOVE):]
                self.display()
                self.douban.unrate_music(self.playingsong)
                self.playingsong['like'] = 0
                self.noti.send_notify(self.playingsong, '取消标记红心')
        self.lock_rate = False

    def set_loop(self):
        '''设置单曲循环'''
        if self.lock_loop:
            self.noti.send_notify(self.playingsong, '停止单曲循环')
            self.lock_loop = False
        else:
            self.noti.send_notify(self.playingsong, '单曲循环')
            self.lock_loop = True

    def set_url(self):
        '''打开豆瓣网页'''
        import webbrowser
        url = "http://music.douban.com" + \
            self.playingsong['album'].replace('\/', '/')
        webbrowser.open(url)

    def set_quit(self):
        '''退出播放'''
        self.q = True
        self.player.quit()
        subprocess.call('echo -e "\033[?25h";clear', shell=True)
        logger.debug('Terminal reset.')
        # store the token and the default info
        self.douban.login_data.update({'volume': self._volume,
                                       'channel': self._channel})
        logger.info(self.douban.login_data)
        db_config.save_config(self.history, self.douban.login_data)
        sys.exit(0)

    @info('正在加载请稍后...')
    def set_channel(self):
        '''开始播放'''
        if self._channel == self.displayline:
            return
        self._channel = self.displayline
        self.douban.set_channel(self._channel)  # 对douban的post_data修改频道
        self.get_playlist()
        self.lock_loop = False
        self.lock_start = True
        self.player.quit()
        self.play()

    @info('正在加载请稍后...')
    def set_next(self):
        '''开始下一曲'''
        if self.player.is_alive:
            self.lock_loop = False
            self.lock_start = True
            self.player.quit()
            if self.state != 3:
                self.playlist = self.douban.skip_song(self.playingsong)
            self.play()

    @info('不再播放，切换下一首...')
    def set_bye(self):
        '''不再播放并进入下一曲'''
        if self.playingsong:
            self.lock_start = True  # 每个play前需self.start置0
            self.player.quit()
            self.playlist = self.douban.bye(self.playingsong)
            self.play()

    @info('正在查找歌词...')
    def set_lrc(self):
        '''显示歌词'''
        self.state = 1
