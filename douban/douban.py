#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
豆瓣fm主程序
"""
# local
import cli              # ui
import douban_token     # network
import getch            # getchar
import player           # player
import notification     # desktop notification
import config           # config
from colors import *    # colors
# system
import subprocess
import threading
import time
import os
import sys
import tempfile
import logging
import cPickle as pickle

# root logger config
logging.basicConfig(
    format="%(asctime)s - \
[%(process)d]%(filename)s:%(lineno)d - %(levelname)s: %(message)s",
    datefmt='%Y-%m-%d %H:%I:%S',
    filename=os.path.expanduser('~/.doubanfm.log'),
    level=logging.WARNING
)

# Set up our own logger
logger = logging.getLogger('doubanfm')
logger.setLevel(logging.INFO)


class Win(cli.Cli):
    '''窗体及播放控制'''
    PATH_HISTORY = os.path.expanduser('~/.douban_history')
    PATH_TOKEN = os.path.expanduser('~/.douban_token.txt')
    KEYS = {
        'UP': 'k',
        'DOWN': 'j',
        'TOP': 'g',
        'BOTTOM': 'G',
        'OPENURL': 'w',
        'RATE': 'r',
        'NEXT': 'n',
        'BYE': 'b',
        'QUIT': 'q',
        'PAUSE': 'p',
        'LOOP': 'l',
        'MUTE': 'm',
        'LRC': 'o',
        'HELP': 'h'
        }
    FNULL = open(os.devnull, 'w')
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

        try:
            with open(self.PATH_HISTORY, 'r') as f:
                self.history = pickle.load(f)
        except IOError:
            self.history = []

        self.douban = douban

        # default volume
        self._volume = douban.default_volume

        # player controler
        self._player_exit_event = threading.Event()
        self.player = player.MPlayer(self._player_exit_event, self._volume)

        # 快捷键配置
        config.get_config(self.KEYS)

        self.TITLE += \
            yellow(' Douban Fm ') if not self.douban.lastfm\
            else yellow(' Last.fm ')

        self.TITLE += '\ ' + self.douban.user_name + ' >>\r'

        # 桌面通知
        self._tempdir = tempfile.mkdtemp()
        self.cover_file = None
        self.has_cover = False

        # 存储歌曲信息
        self._lines = self.douban.channels
        self._channel = self.douban.default_channel
        self.playingsong = None
        self.playlist = None
        self.find_lrc = False
        self.lrc_dict = {}  # 歌词

        super(Win, self).__init__(self._lines)

        # 启动自动播放
        self.markline = self.displayline = self._channel
        self.lock_start = True
        self.SUFFIX_SELECTED = '正在加载请稍后...'
        self.display()

        self.thread(self.play)          # 播放控制
        self.thread(self.watchdog)      # 播放器守护线程
        self.thread(self.display_time)  # 时间显示
        self.run()

    def thread(self, target, args=()):
        '''启动新线程'''
        threading.Thread(target=target, args=args).start()


    def init_notification(self):
        '''第一次桌面通知时加入图片'''
        old_title = self.playingsong['title']
        self.cover_file = tempfile.NamedTemporaryFile(
                suffix='.jpg', dir=self._tempdir)
        if not self.douban.get_pic(self.playingsong, self.cover_file.name):
            return
        title = self.playingsong['title']
        if old_title != title:
            # 已切换至下一首歌
            return
        self.has_cover = True
        content = self.playingsong['artist'] + ' - ' \
            + self.playingsong['albumtitle']
        notification.send_notification(title, content, self.cover_file.name)

    def send_notify(self, content):
        title = self.playingsong['title']
        if self.has_cover:
            notification.send_notification(title, content, self.cover_file.name)
        else:
            notification.send_notification(title, content)

    def display_lrc(self):
        '''歌词显示线程'''
        # TODO
        if not self.find_lrc:
            self.find_lrc = True
            self.lrc_dict = self.douban.get_lrc(self.playingsong)
        if self.lrc_dict:
            Lrc(self.lrc_dict, self)
        else:
            self.state = 0

    def get_title(self, songtime=None, kbps=None, vol=None, state=None):
        pass

    def display_time(self):
        '''时间/音量显示线程'''
        length = len(self.TITLE)
        rest_time = 0
        while not self.q:
            if self.lock_pause:
                continue
            if self.player.is_alive:
                songtime = self.player.time_pos
                if songtime:
                    self.songtime = songtime
                # 181s -> 03:01
                rest_time = int(self.playingsong['length']) - self.songtime - 1
                minute = int(rest_time) / 60
                sec = int(rest_time) % 60
                show_time = str(minute).zfill(2) + ':' + str(sec).zfill(2)

                title_pro = '' if self.playingsong['kbps'] == '64' else self.PRO
                title_kbps = self.playingsong['kbps'] + 'kbps'
                title_time = cyan(show_time)
                title_rate = red(self.RATE[int(round(self.playingsong['rating_avg'])) - 1])
                title_vol = red('✖') if self.lock_muted else str(self._volume) + '%'
                title_loop = red('↺') if self.lock_loop else red('→')
                title = [
                    title_pro,
                    title_kbps,
                    title_time,
                    title_rate,
                    title_vol,
                    title_loop
                ]
                self.TITLE = \
                    self.TITLE[:length - 1] + ' ' + ' '.join(title) + '\r'
                self.display()
            else:
                self.TITLE = self.TITLE[:length]
            time.sleep(1)

    def display(self):
        '''显示主控制界面'''
        if self.state == 0:
            cli.Cli.display(self)

    def change_volume(self, increment):
        '''调整音量大小'''
        if increment == 1:
            self._volume += 5
        else:
            self._volume -= 5
        self._volume = max(min(self._volume, 100), 0)
        self.lock_muted = False if self._volume else True
        self.player.set_volume(self._volume)

    def mute(self):
        '''静音'''
        if self.lock_muted:
            self.lock_muted = False
            if self._volume == 0:
                self._volume = 10
            volume = self._volume
        else:
            self.lock_muted = True
            volume = 0
        self.player.set_volume(volume)

    def watchdog(self):
        '''守护线程，检查歌曲是否播放完毕'''
        while not self.q:
            if not self.player.is_alive:
                # Reduce some CPU use (useful when player not yet started)
                time.sleep(1)
            logger.debug('Wait till player exit.')
            self._player_exit_event.wait()      # Wait for event
            self._player_exit_event.clear()     # Clear the event
            logger.debug('Noticed player exit.')
            # If self.q (about to quit), just quit
            # If some thread has already called play(), just pass
            if not self.q and not self.lock_start:
                self.thread(self.douban.submit_music, args=(self.playingsong,))
                self.play()

    def get_playlist(self):
        self.playlist = self.douban.get_playlist(self._channel)

    def get_song(self):
        if not self.playlist:
            self.get_playlist()
        return self.playlist.pop(0)

    def play(self):
        '''播放歌曲'''
        self.lock_start = True
        self.find_lrc = False
        self.lrc_dict = {}  # 歌词清空
        self.songtime = 0  # 重置歌曲时间
        self.playingsong = self.get_song()
        if not self.lock_loop:
            self.playingsong['time'] = time.strftime("%Y-%m-%d %H:%M:%S",
                                                     time.localtime())
            self.history.insert(0, self.playingsong)
        song = self.playingsong

        self.thread(self.init_notification)  # 桌面通知

        if song['like'] == 1:
            love = self.love + ' '
        else:
            love = ''
        title = green(song['title'])
        albumtitle = yellow(song['albumtitle'])
        artist = white(song['artist'])
        public_time = song['public_time'] or ''
        self.SUFFIX_SELECTED = (
            love +
            title + ' •' +
            albumtitle + ' •' +
            artist + ' ' +
            public_time
        ).replace('\\', '')

        logger.debug("Start playing %s - %s.", song['artist'], song['title'])
        self.player.start(song['url'].replace('\\', ''))

        self.lock_pause = False
        self.display()

        if self.state == 1:  # 获取歌词
            self.thread(self.display_lrc)
        self.lock_start = False
        # Will do nothing if not log into Last.fm
        self.thread(self.douban.scrobble_now_playing)

    def pause(self):
        '''暂停歌曲'''
        if self.lock_pause:
            self.lock_pause = False
            self.send_notify(content='开始播放')
        else:
            self.send_notify(content='暂停播放')
            self.lock_pause = True
        self.player.pause()

    def run(self):
        '''主交互逻辑 (key event loop)'''
        while True:
            self.display()
            c = getch.getch()
            if not self.state == 1:  # 歌词模式下除了方向键都可以用
                if c == self.KEYS['UP']:
                    self.updown(-1)
                elif c == self.KEYS['DOWN']:
                    self.updown(1)
                elif c == self.KEYS['TOP']:      # g键返回顶部
                    self.markline = 0
                    self.topline = 0
                elif c == self.KEYS['BOTTOM']:   # G键返回底部
                    self.markline = self.screen_height
                    self.topline = len(self._lines) - self.screen_height - 1
            if c == self.KEYS['HELP']:     # help界面
                self.state = 2
                Help(self)
            elif c == self.KEYS['LRC']:      # o歌词
                self.set_lrc()
                self.state = 1
                self.thread(self.display_lrc)
            elif c == 'e' and self.state == 0:
                self.state = 3
                History(self)
            elif c == self.KEYS['RATE']:     # r标记红心/取消标记
                self.thread(self.set_rate)
            elif c == self.KEYS['NEXT']:     # n下一首
                self.set_next()
            elif c == ' ':                   # 空格选择频道,播放歌曲
                if self.markline + self.topline != self.displayline:
                    self.displaysong()
                    self.set_play()
            elif c == self.KEYS['OPENURL']:  # l打开当前播放歌曲豆瓣页
                self.set_url()
            elif c == self.KEYS['BYE']:      # b不再播放
                self.set_bye()
            elif c == self.KEYS['PAUSE']:    # p暂停
                self.pause()
            elif c == self.KEYS['MUTE']:     # m静音
                self.mute()
            elif c == self.KEYS['LOOP']:     # l单曲循环
                self.set_loop()
            elif c == self.KEYS['QUIT']:     # q退出程序
                if self.state == 0:
                    self.state = 4
                    Quit(self)
                else:
                    self.state = 0
            elif c == '=' or c == '+':       # 提高音量
                self.change_volume(1)
            elif c == '-' or c == '_':       # 降低音量
                self.change_volume(-1)

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
        while(self.lock_rate):
            if self.q:
                return
        self.lock_rate = True
        if self.playingsong:
            if not self.playingsong['like']:
                self.SUFFIX_SELECTED = self.love + self.SUFFIX_SELECTED
                self.display()
                self.douban.rate_music(self.playingsong)
                self.playingsong['like'] = 1
                self.send_notify(content='标记红心')
            else:
                self.SUFFIX_SELECTED = self.SUFFIX_SELECTED[len(self.love):]
                self.display()
                self.douban.unrate_music(self.playingsong)
                self.playingsong['like'] = 0
                self.send_notify(content='取消标记红心')
        self.lock_rate = False

    def set_loop(self):
        '''设置单曲循环'''
        if self.lock_loop:
            self.send_notify(content='停止单曲循环')
            self.lock_loop = False
        else:
            self.send_notify(content='单曲循环')
            self.lock_loop = True

    def set_url(self):
        '''打开豆瓣网页'''
        import webbrowser
        url = "http://music.douban.com" + \
            self.playingsong['album'].replace('\/', '/')
        webbrowser.open(url)
        self.display()

    def set_quit(self):
        '''退出播放'''
        self.q = True
        self.player.quit()
        subprocess.call('echo -e "\033[?25h";clear', shell=True)
        logger.debug('Terminal reset.')
        try:
            if self.cover_file is not None:
                self.cover_file.close()
            os.rmdir(self._tempdir)
            logger.debug('Temporary files removed.')
        except OSError:
            pass
        # store the history of playlist
        with open(self.PATH_HISTORY, 'w') as f:
            pickle.dump(self.history, f)
        logger.debug('History saved.')
        # stroe the token and the default info
        with open(self.PATH_TOKEN, 'r') as f:
            data = pickle.load(f)
            data['volume'] = self._volume
            data['channel'] = self._channel
        with open(self.PATH_TOKEN, 'w') as f:
            pickle.dump(data, f)
        logger.debug('Settings saved.')
        sys.exit(0)

    @info('正在加载请稍后...')
    def set_play(self):
        '''开始播放'''
        logger.debug(str(self.displayline) + str(self._channel))
        self._channel = self.displayline
        self.lock_start = True
        # self.playingsong = {}
        self.player.quit()
        self._channel = self.displayline
        self.get_playlist()
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
            if self.cover_file is not None:
                self.cover_file.close()
            self.has_cover = False
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


class Lrc(cli.Cli):
    '''歌词显示界面'''
    def __init__(self, lrc_dict, win):
        self.win = win
        self.lrc_dict = lrc_dict

        self.playingsong = win.playingsong

        # 歌曲总长度
        self.length = int(win.playingsong['length'])
        # 歌曲播放秒数
        self.song_time = self.win.songtime

        self.sort_lrc_dict = sorted(lrc_dict.iteritems(), key=lambda x: x[0])
        self.lines = [line[1] for line in self.sort_lrc_dict if line[1]]

        subprocess.call('clear')  # 清屏

        self.markline = self.find_line()
        self.topline = 0
        self.display()
        self.display_line()

    def find_line(self):
        '''第一次载入时查找歌词'''
        for now_time in reversed(range(self.song_time)):
            locate = [index for index, i in enumerate(self.sort_lrc_dict)
                      if i[0] == now_time]  # 查找歌词在self.sort_lrc_dict中的位置
            if locate:
                return locate[0]
        return 0

    def __del__(self):
        self.win.state = 0

    def display_line(self):
        '''显示歌词'''
        while self.win.state == 1:
            if self.playingsong != self.win.playingsong:
                break
            self.display()
            self.song_time = self.win.songtime
            if self.song_time < self.length:
                # 查找歌词在self.sort_lrc_dict中的位置
                locate = \
                    [index for index, i in enumerate(self.sort_lrc_dict)
                     if i[0] == self.song_time]
                if locate:
                    self.markline = locate[0]
                    self.display()
                time.sleep(1)

    def display(self):
        '''输出界面'''
        self.screen_height, self.screen_width = self.linesnum()  # 屏幕显示行数
        subprocess.call('clear')
        print
        print self.win.TITLE
        print
        for linenum in range(self.screen_height - 2):
            if self.screen_height/2 - linenum > self.markline - self.topline or \
                    linenum - self.screen_height/2 >= len(self.lines) - self.markline:
                print '\r'
            else:
                line = self.lines[self.markline - (self.screen_height/2 - linenum)]
                line = line.strip()
                l = self.center_num(line)
                flag_num = (self.screen_width - l) / 2
                if linenum == self.screen_height/2:
                    i = blue(line)
                    print ' ' * flag_num + i + '\r'
                else:
                    print ' ' * flag_num + line + '\r'
        print '\r'

        # 歌曲信息居中
        song = self.win.playingsong
        tmp = (
            song['title'] +
            song['albumtitle'] +
            song['artist'] +
            song['public_time']
        ).replace('\\', '').strip()
        tmp = unicode(tmp, 'utf-8')
        l = self.center_num(tmp) + 7  # 7个固定字符
        if song['like']:
            l += 2
        flag_num = (self.screen_width - l) / 2
        self.title = ' ' * flag_num + self.win.SUFFIX_SELECTED + '\r'  # 歌词页面标题
        print self.title


class Help(cli.Cli):
    '''帮助界面，查看快捷键'''
    def __init__(self, win):
        self.win = win
        self.win.thread(self.display_help)

    def display_help(self):
        while self.win.state == 2:
            self.display()
            time.sleep(1)

    def __del__(self):
        self.win.state = 0

    def display(self):
        keys = self.win.KEYS
        subprocess.call('clear', shell=True)
        print
        print self.win.TITLE
        print
        print ' '*5 + green('移动') + ' '*17 + green('音乐') + '\r'
        print ' '*5 + '[%(DOWN)s] ---> 下          [space] ---> 播放' % keys + '\r'
        print ' '*5 + '[%(UP)s] ---> 上          [%(OPENURL)s] ---> 打开歌曲主页' % keys + '\r'
        print ' '*5 + '[%(TOP)s] ---> 移到最顶    [%(NEXT)s] ---> 下一首' % keys + '\r'
        print ' '*5 + '[%(BOTTOM)s] ---> 移到最底    [%(RATE)s] ---> 喜欢/取消喜欢' % keys + '\r'
        print ' '*26 + '[%(BYE)s] ---> 不再播放' % keys + '\r'

        print ' '*5 + green('音量') + ' '*17 + '[%(PAUSE)s] ---> 暂停' % keys + '\r'
        print ' '*5 + '[=] ---> 增          [%(QUIT)s] ---> 退出' % keys + '\r'
        print ' '*5 + '[-] ---> 减          [%(LOOP)s] ---> 单曲循环' % keys + '\r'
        print ' '*5 + '[%(MUTE)s] ---> 静音' % keys + '\r'

        print
        print ' '*5 + green('歌词') + '\r'
        print ' '*5 + '[%(LRC)s] ---> 歌词' % keys + '\r'


class Quit(Help):
    '''退出界面'''
    def __init__(self, win):
        self.win = win
        subprocess.check_call('clear', shell=True)
        self.screen_height, self.screen_width = self.linesnum()  # 屏幕显示行数
        self.display()
        self.run()

    def display(self):
        for i in range(self.screen_height):
            if i == self.screen_height / 2:
                print ' ' * ((self.screen_width - 18)/2) \
                    + red('Are you sure? (Y/n)'),
            else:
                print

    def run(self):
        '''界面执行程序'''
        c = getch.getch()
        if c == 'y' or c == 'Y' or ord(c) == 13:
            self.win.set_quit()


class History(cli.Cli):
    '''历史记录'''
    def __init__(self, win):
        self.win = win
        self.KEYS = self.win.KEYS
        # the playlist of the history
        self.love = red(' ♥ ')
        self.screen_height, self.screen_width = self.linesnum()

        # 3个tab, playlist thistory rate
        # 分别对应状态 0 1 2
        self.state = 0
        self.play_tag = '♬♬♬♬♬♬'
        self.subtitle = [
                on_cyan('Playlist') + ' '*5 + 'History' + ' '*5 + 'Rate',
                'Playlist' + ' '*5 + on_cyan('History') + ' '*5 + 'Rate',
                'Playlist' + ' '*5 + 'History' + ' '*5 + on_cyan('Rate')
                ]
        # hitory 使用win.history
        self.rate = []
        self.playlist = []

        self.get_lines()
        super(History, self).__init__(self.lines)
        # 默认箭头指向第二排
        # 为tab留出空余
        self.markline = 1
        self.win.thread(self.display_help)
        self.run()

    def get_lines(self):
        """因为历史列表动态更新,需要刷新"""
        self.lines = []
        width = self.screen_width - 24
        if self.state == 0:
            # 播放列表
            for index, i in enumerate(self.win.playlist):
                line = i['title'] if len(i['title']) < width else i['title'][:width]
                line = green(line)
                line = str(index) + ' ' + line
                if i['like'] == 1:
                    line += self.love
                if i == self.win.playingsong:
                    line += self.play_tag
                self.lines.append(line)
        elif self.state == 1:
            # 历史列表
            for index, i in enumerate(self.win.history):
                line = i['title'] if len(i['title']) < width else i['title'][:width]
                line = green(line)
                line = i['time'][5:] + ' ' + line
                if i['like'] == 1:
                    line += self.love
                if i == self.win.playingsong:
                    line += self.play_tag
                self.lines.append(line)
        elif self.state == 2:
            # 红心列表
            self.rate = []
            for i in reversed(self.win.history):
                if i['like'] == 1:
                    if i in self.rate:
                        self.rate.remove(i)
                        self.rate.insert(0, i)
                    else:
                        self.rate.insert(0, i)
            for index, i in enumerate(self.rate):
                line = i['title'] if len(i['title']) < width else i['title'][:width]
                line = green(line)
                line = str(index) + ' ' + line + self.love
                if i == self.win.playingsong:
                    line += self.play_tag

                self.lines.append(line)
        self.lines.insert(0, self.subtitle[self.state])

    def display_help(self):
        while self.win.state == 3:
            self.get_lines()
            self.display()
            time.sleep(1)

    def display(self):
        self.TITLE = self.win.TITLE
        cli.Cli.display(self)

    def run(self):
        '''界面执行程序'''
        while True:
            self.display()
            c = getch.getch()
            if c == self.KEYS['UP'] and self.markline != 1:
                self.updown(-1)
            elif c == self.KEYS['DOWN']:
                self.updown(1)
            elif c == self.KEYS['QUIT']:
                self.win.state = 0
                break
            elif c == ' ':
                self.playsong()
            elif c == self.KEYS['TOP']:      # g键返回顶部
                self.markline = 1
                self.topline = 0
            elif c == self.KEYS['BOTTOM']:   # G键返回底部
                if len(self.lines) < self.screen_height:
                    self.markline = len(self.lines) - 1
                else:
                    self.markline = self.screen_height
                    self.topline = len(self.lines) - self.screen_height - 1
            elif c == 'h':
                self.state -= 1 if self.state != 0 else -2
                self.get_lines()
            elif c == 'l':
                self.state += 1 if self.state != 2 else -2
                self.get_lines()

    def playsong(self):
        # get the line num of the list
        self.displaysong()
        if self.state == 0:
            return
        elif self.state == 1:
            # 如果在历史列表里播放,只在win.playlist里插入一首歌曲
            # 播放完毕继续
            self.win.playlist.insert(
                0, self.win.history[self.markline + self.topline - 1]
            )
        elif self.state == 2:
            self.win.playlist = self.rate[self.displayline-1:]
        self.win.set_next()


def main():
    douban = douban_token.Doubanfm()
    douban.init_login()  # 登录
    Win(douban)

if __name__ == '__main__':
    main()
