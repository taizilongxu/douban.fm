#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
豆瓣FM主程序
"""
import cli  # UI
import douban_token  # network
import getch  # get char
import subprocess
from termcolor import colored
import notification
import threading
import time
import os
import tempfile
import ConfigParser
import logging
import errno
import pickle

# 设置logger
logging.basicConfig(
    format='%(asctime)s - [%(process)d]%(filename)s:%(lineno)d - %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%I:%S',
    filename=os.path.expanduser('~/.doubanfm.log'),
    level=logging.DEBUG
)
logger = logging.getLogger()


class Win(cli.Cli):
    '''窗体及播放控制'''
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

    def __init__(self, douban):
        # 线程锁
        self.lock_start = False  # 播放锁,play之前需要加
        self.lock_lrc = False    # 是否显示歌词
        self.lock_rate = False   # 加心锁
        self.lock_help = False   # 是否现实帮助
        self.lock_history = False  # 是否现实历史记录
        self.lock_loop = False   # 循环锁
        self.lock_muted = False  # 静音锁
        self.lock_pause = True   # 暂停锁
        self.q = False           # 退出
        self.songtime = 0        # 歌曲时间
        self.playingsong = None  # 当前播放歌曲
        self.history = []

        self.volume = douban.default_volume  # 默认音量
        self.get_config()  # 快捷键配置
        self.douban = douban


        self.TITLE += \
            colored(' Douban Fm ', 'yellow') if not self.douban.lastfm\
            else colored(' Last.fm ', 'yellow')
        PRO = '' if self.douban.pro == 0 else colored(' PRO ', attrs=['reverse'])

        self.TITLE += '\ ' + self.douban.user_name + PRO + ' >>\r'

        self.lrc_dict = {}  # 歌词

        self._tempdir = tempfile.mkdtemp()
        self.cover_file = None
        self.has_cover = False

        # subprocess
        self.p = None

        super(Win, self).__init__(self.douban.lines)

        # 启动自动播放
        self.markline = self.displayline = self.douban.default_channel
        self.lock_start = True
        self.SUFFIX_SELECTED = '正在加载请稍后...'
        self.display()
        self.lock_start = False
        while True:
            try:
                # 设置默认频率
                self.douban.set_channel(self.douban.channels[self.markline]['channel_id'])
                break
            except IndexError as e:
                # 默认频道不存在，重置为红心兆赫
                if self.markline == 0:
                    raise e
                self.markline = self.displayline = 0
            except KeyError:
                # 无红心兆赫进入下一个频道
                self.markline += 1
                self.displayline += 1
        self.thread(self.play)          # 播放控制
        self.thread(self.watchdog)      # 播放器守护线程
        self.thread(self.display_time)  # 时间显示
        self.run()

    def thread(self, target):
        '''启动新线程'''
        threading.Thread(target=target).start()

    def get_config(self):
        '''获取配置'''
        config = ConfigParser.ConfigParser()
        with open(os.path.expanduser('~/.doubanfm_config'), 'r') as cfgfile:
            config.readfp(cfgfile)
            options = config.options('key')
            for option in options:
                option = option.upper()
                if option in self.KEYS:
                    self.KEYS[option] = config.get('key', option)

    def init_notification(self):
        '''第一次桌面通知时加入图片'''
        old_title = self.douban.playingsong['title']
        self.cover_file = tempfile.NamedTemporaryFile(suffix='.jpg', dir=self._tempdir)
        if not self.douban.get_pic(self.cover_file.name):
            return
        title = self.douban.playingsong['title']
        if old_title != title:
            # 已切换至下一首歌
            return
        self.has_cover = True
        content = self.douban.playingsong['artist'] + ' - ' \
            + self.douban.playingsong['albumtitle']
        notification.send_notification(title, content, self.cover_file.name)

    def send_notify(self, content):
        title = self.douban.playingsong['title']
        if self.has_cover:
            notification.send_notification(title, content, self.cover_file.name)
        else:
            notification.send_notification(title, content)

    def display_lrc(self):
        '''歌词显示线程'''
        self.lrc_dict = self.douban.get_lrc()
        if self.lrc_dict:
            Lrc(self.lrc_dict, self)
        else:
            self.lock_lrc = False

    def display_time(self):
        '''时间/音量显示线程'''
        length = len(self.TITLE)
        rest_time = 0
        while True:
            if self.q:  # 退出
                break
            if self.lock_pause:
                continue
            if self.p and self.douban.playingsong:
                self.songtime = self.get_songtime()
                rest_time = \
                    int(self.douban.playingsong['length']) - self.songtime
                minute = int(rest_time) / 60
                sec = int(rest_time) % 60
                show_time = str(minute).zfill(2) + ':' + str(sec).zfill(2)

                self.TITLE = \
                    self.TITLE[:length - 1] + ' ' + \
                    self.douban.playingsong['kbps'] + 'kbps ' + \
                    colored(show_time, 'cyan') + ' rate:' + \
                    colored(self.RATE[int(round(self.douban.playingsong['rating_avg'])) - 1], 'red') + ' vol:'
                self.TITLE += colored('✖', 'red') if self.lock_muted else str(self.volume) + '%'
                self.TITLE += '  ' + colored('↺', 'red') if self.lock_loop else '  ' + colored('→', 'red')
                self.TITLE += '\r'
                self.display()
            else:
                self.TITLE = self.TITLE[:length]
            time.sleep(1)

    def perform_command(self, p, cmd, expect):
        '''myplayer 读取mplayer输出'''
        import select
        try:
            p.stdin.write(cmd + '\n') # there's no need for a \n at the beginning
        except IOError,e:
            logger.debug(e)
            return
        while select.select([p.stdout], [], [], 0.5)[0]:
            output = p.stdout.readline()
            split_output = output.split(expect + '=', 1)
            if len(split_output) == 2 and split_output[0] == '': # we have found it
                value = split_output[1]
                return value.rstrip()
        return

    def get_songtime(self):
        '''在mplayer里获取歌曲播放时间'''
        song_time = self.perform_command(self.p, 'get_time_pos', 'ANS_TIME_POSITION')
        if song_time:
            # logger.info(song_time)
            return int(round(float(song_time)))
        else:
            return self.songtime

    def display(self):
        '''显示主控制界面'''
        if not self.lock_history and not self.lock_lrc and self.lock_start and not self.lock_help:
            cli.Cli.display(self)

    def change_volume(self, increment):
        '''调整音量大小'''
        if increment == 1:
            self.volume += 5
        else:
            self.volume -= 5
        self.volume = max(min(self.volume, 100),0)
        self.lock_muted = True if self.volume == 0 else False
        try:
            self.p.stdin.write('volume %d 1\n' % self.volume)
        except IOError as e:
            if e.errno != errno.EPIPE:
                raise e

    def mute(self):
        '''静音'''
        if self.lock_muted:
            self.lock_muted = False
            if self.volume == 0:
                self.volume = 10
            volume = self.volume
        else:
            self.lock_muted = True
            volume = 0
        try:
            self.p.stdin.write('volume %d 1\n' % volume)
        except IOError as e:
            if e.errno != errno.EPIPE:
                raise e

    def watchdog(self):
        '''守护线程，检查歌曲是否播放完毕'''
        while True:
            if self.q:
                break
            if self.p is not None:
                logger.debug("Watching mplayer[%d]", self.p.pid)
                self.p.wait()
                if self.p.returncode is not None:
                    logger.debug("mplayer exits with code %d", self.p.returncode)
                if self.q:
                    break
                if self.p.returncode == 0 and not self.lock_loop and self.douban.playingsong:
                    self.thread(self.douban.end_music)  # 发送完成
                    self.thread(self.douban.submit_current_song)
                if self.lock_start:
                    self.play()
            time.sleep(1)

    def play(self):
        '''播放歌曲'''
        self.lrc_dict = {}  # 歌词清空
        self.songtime = 0  # 重置歌曲时间
        if not self.lock_loop:
            self.douban.get_song()
        song = self.douban.playingsong
        self.history.append(self.douban.playingsong)

        self.thread(self.init_notification)  # 桌面通知

        if song['like'] == 1:
            love = self.love
        else:
            love = ''
        title = colored(song['title'], 'green')
        albumtitle = colored(song['albumtitle'], 'yellow')
        artist = colored(song['artist'], 'white')
        self.SUFFIX_SELECTED = (love + title + ' •' + albumtitle + ' •' + artist + ' ' + song['public_time']).replace('\\', '')

        cmd = 'mplayer -slave -nolirc -quiet -softvol -volume {volume} {song_url}'
        volume = 0 if self.lock_muted else self.volume
        cmd = cmd.format(volume=volume, song_url=song['url'])
        logger.debug('Starting process: ' + cmd)
        self.p = subprocess.Popen(
            cmd,
            shell=True,
            # I/O 重定向
            # 不在命令中直接使用管道符，避免产生多余的 sh 进程
            stdin=subprocess.PIPE,      # open a pipe for input
            stdout=subprocess.PIPE,          # >/dev/null
            stderr=subprocess.STDOUT    # 2>&1
        )
        self.lock_pause = False
        self.display()

        if self.lock_lrc:  # 获取歌词
            self.thread(self.display_lrc)
        self.lock_start = True
        # Will do nothing if not log into Last.fm
        self.thread(self.douban.scrobble_now_playing)

    def pause_play(self):
        '''暂停歌曲'''
        if self.lock_pause:
            self.lock_pause = False
            self.send_notify(content='开始播放')
        else:
            self.send_notify(content='暂停播放')
            self.lock_pause = True
        try:
            self.p.stdin.write('pause\n')
        except IOError as e:
            if e.errno != errno.EPIPE:
                raise e

    def kill_mplayer(self):
        '''结束mplayer'''
        try:
            self.p.stdin.write('quit 0\n')
        except IOError as e:
            if e.errno != errno.EPIPE:
                raise e


    def run(self):
        '''主交互逻辑 (key event loop)'''
        while True:
            self.display()
            c = getch.getch()
            if not self.lock_lrc:  # 歌词模式下除了方向键都可以用
                if c == self.KEYS['UP']:
                    self.updown(-1)
                elif c == self.KEYS['DOWN']:
                    self.updown(1)
                elif c == self.KEYS['TOP']:      # g键返回顶部
                    self.markline = 0
                    self.topline = 0
                elif c == self.KEYS['BOTTOM']:   # G键返回底部
                    self.markline = self.screen_height
                    self.topline = len(self.lines) - self.screen_height - 1
            if c == self.KEYS['HELP']:     # help界面
                Help(self)
            elif c == self.KEYS['LRC']:      # o歌词
                self.set_lrc()
                self.thread(self.display_lrc)
            elif c =='e':
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
                self.pause_play()
            elif c == self.KEYS['MUTE']:     # m静音
                self.mute()
            elif c == self.KEYS['LOOP']:     # l单曲循环
                self.set_loop()
            elif c == self.KEYS['QUIT']:     # q退出程序
                if self.lock_lrc:
                    self.lock_lrc = False
                elif self.lock_help :
                    self.lock_help = False
                elif self.lock_history:
                    self.lock_history = False
                else:
                    self.set_quit()
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
        if self.douban.playingsong:
            if not self.douban.playingsong['like']:
                self.SUFFIX_SELECTED = self.love + self.SUFFIX_SELECTED
                self.display()
                self.douban.rate_music()
                self.douban.playingsong['like'] = 1
                self.send_notify(content='标记红心')
            else:
                self.SUFFIX_SELECTED = self.SUFFIX_SELECTED[len(self.love):]
                self.display()
                self.douban.unrate_music()
                self.douban.playingsong['like'] = 0
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
        url = "http://music.douban.com" + self.douban.playingsong['album'].replace('\/', '/')
        webbrowser.open(url)
        self.display()

    def set_quit(self):
        '''退出播放'''
        self.q = True
        if self.lock_start:
            self.kill_mplayer()
        subprocess.call('echo -e "\033[?25h";clear', shell=True)
        try:
            if self.cover_file is not None:
                self.cover_file.close()
            os.rmdir(self._tempdir)
        except OSError:
            pass
        path_token = os.path.expanduser('~/.douban_token.txt')
        with open(path_token, 'r') as f:
            data = pickle.load(f)
            data['volume'] = self.volume
            data['channel'] = self.displayline
        with open(path_token, 'w') as f:
            pickle.dump(data, f)
        exit()

    @info('正在加载请稍后...')
    def set_play(self):
        '''开始播放'''
        self.lock_start = False
        if self.douban.playingsong:
            self.douban.playingsong = {}
            self.kill_mplayer()
        self.douban.set_channel(self.douban.channels[self.markline + self.topline]['channel_id'])
        self.douban.get_playlist()
        self.play()

    @info('正在加载请稍后...')
    def set_next(self):
        '''开始下一曲'''
        if self.douban.playingsong:
            self.lock_loop = False
            self.lock_start = False
            self.kill_mplayer()
            self.douban.skip_song()
            self.douban.playingsong = {}
            if self.cover_file is not None:
                self.cover_file.close()
            self.has_cover = False
            self.play()

    @info('不再播放，切换下一首...')
    def set_bye(self):
        '''不再播放并进入下一曲'''
        if self.douban.playingsong:
            self.lock_start = False  # 每个play前需self.start置0
            self.kill_mplayer()
            self.douban.bye()
            self.douban.playingsong = {}
            self.play()

    @info('正在查找歌词...')
    def set_lrc(self):
        '''显示歌词'''
        self.lock_lrc = True


class Lrc(cli.Cli):
    '''歌词显示界面'''
    def __init__(self, lrc_dict, win):
        self.win = win
        self.lrc_dict = lrc_dict

        self.playingsong = win.douban.playingsong

        # 歌曲总长度
        self.length = int(win.douban.playingsong['length'])
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
            locate = [index for index, i in enumerate(self.sort_lrc_dict) if i[0] == now_time]  # 查找歌词在self.sort_lrc_dict中的位置
            if locate:
                return locate[0]
        return 0

    def display_line(self):
        '''显示歌词'''
        while self.win.lock_lrc:
            if self.playingsong != self.win.douban.playingsong:
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

    def is_cn_char(self, i):
        '''判断中文字符'''
        return 0x4e00 <= ord(i) < 0x9fa6

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
                print
            else:
                line = self.lines[self.markline - (self.screen_height/2 - linenum)].strip()
                l = self.center_num(line)
                flag_num = (self.screen_width - l) / 2
                if linenum == self.screen_height/2:
                    i = colored(line, 'blue')
                    print ' ' * flag_num + i + '\r'
                else:
                    print ' ' * flag_num + line + '\r'
        print '\r'

        # 歌曲信息居中
        song = self.win.douban.playingsong
        tmp = (song['title'] + song['albumtitle'] + song['artist'] + song['public_time']).replace('\\', '').strip()
        tmp = unicode(tmp, 'utf-8')
        l = self.center_num(tmp) + 7  # 7个固定字符
        if song['like']:
            l += 2
        flag_num = (self.screen_width - l) / 2
        self.title = ' ' * flag_num + self.win.SUFFIX_SELECTED + '\r'  # 歌词页面标题
        print self.title

    # 需要考虑中文和英文的居中
    def center_num(self, tmp):
        l = 0
        for i in tmp:
            l += 2 if self.is_cn_char(i) else 1
        return l


class Help(cli.Cli):
    '''帮助界面，查看快捷键'''
    def __init__(self, win):
        self.win = win
        self.win.lock_help = True
        self.win.thread(self.display_help)

    def display_help(self):
        while self.win.lock_help:
            self.display()
            time.sleep(1)
        self.win.lock_help = False

    def display(self):
        keys = self.win.KEYS
        subprocess.call('clear', shell=True)
        print
        print self.win.TITLE
        print
        print ' '*5 + colored('移动', 'green') + ' '*17 + colored('音乐', 'green') + '\r'
        print ' '*5 + '[%(DOWN)s] ---> 下          [space] ---> 播放' % keys + '\r'
        print ' '*5 + '[%(UP)s] ---> 上          [%(OPENURL)s] ---> 打开歌曲主页' % keys + '\r'
        print ' '*5 + '[%(TOP)s] ---> 移到最顶    [%(NEXT)s] ---> 下一首' % keys + '\r'
        print ' '*5 + '[%(BOTTOM)s] ---> 移到最底    [%(RATE)s] ---> 喜欢/取消喜欢' % keys + '\r'
        print ' '*26 + '[%(BYE)s] ---> 不再播放' % keys + '\r'

        print ' '*5 + colored('音量', 'green') + ' '*17 + '[%(PAUSE)s] ---> 暂停' % keys + '\r'
        print ' '*5 + '[=] ---> 增          [%(QUIT)s] ---> 退出' % keys + '\r'
        print ' '*5 + '[-] ---> 减          [%(LOOP)s] ---> 单曲循环' % keys + '\r'
        print ' '*5 + '[%(MUTE)s] ---> 静音' % keys + '\r'

        print
        print ' '*5 + colored('歌词', 'green') + '\r'
        print ' '*5 + '[%(LRC)s] ---> 歌词' % keys + '\r'

class History(cli.Cli):
    '''历史记录'''
    def __init__(self, win):
        self.win = win
        self.win.lock_history = True
        self.lines = [i['title'] for i in self.win.history] if self.win.history else []
        super(History, self).__init__(self.lines)
        self.win.thread(self.display_help)
        self.run()
        self.win.lock_history = False

    def display_help(self):
        while self.win.lock_history:
            self.display()
            time.sleep(1)

    def display(self):
        self.TITLE = self.win.TITLE
        cli.Cli.display(self)

    def run(self):
        '''界面执行程序'''
        while True:
            logger.debug('History.run()')
            self.display()
            c = getch.getch()
            if c == 'k':
                self.updown(-1)
            if c == 'j':
                self.updown(1)
            if c == 'q':
                break

def main():
    douban = douban_token.Doubanfm()
    douban.init_login()  #登录
    Win(douban)

if __name__ == '__main__':
    main()
