#!/usr/bin/env python
#-*- encoding: UTF-8 -*-
"""
豆瓣FM主程序
"""
#---------------------------------import------------------------------------
import cli  # UI
import douban_token  # network
import getch  # get char
import subprocess
from termcolor import colored
import threading
import time
import os
import tempfile
import ConfigParser
import platform
try:
    import Foundation
    import objc
    import AppKit
except ImportError:
    pass
#---------------------------------------------------------------------------
class Win(cli.Cli):

    def __init__(self, douban):
        self.KEYS = {
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
            'LRC': 'o'
            }
        self.platform = platform.system()
        self.get_config()
        self.douban = douban
        if self.douban.pro == 0:
            PRO = ''
        else:
            PRO = colored(' PRO ', attrs=['reverse'])
        self.TITLE += self.douban.user_name + ' ' + PRO + ' ' + ' >>\r'
        self.start = 0  # 播放锁,play之前需要加
        self.q = 0  # 退出
        self.lrc_dict = {}  # 歌词
        self.song_time = -1  # 歌曲剩余播放时间
        self.rate = ['★ '*i for i in range(1, 6)]  # 歌曲评分
        self.lrc_display = 0  # 是否显示歌词

        self.lock_rate = 0  # 加心锁
        self.lock_help = 0

        self.pause = True
        self.mplayer_controller = os.path.join(tempfile.mkdtemp(), 'mplayer_controller')
        self.loop = False
        self.is_muted = False  # 是否静音
        os.mkfifo(self.mplayer_controller)
        # 守护线程
        self.thread(self.protect)
        self.thread(self.display_time)
        # self.thread(self.display_lrc)
        super(Win, self).__init__(self.douban.lines)
        # 启动自动播放
        self.start = 1
        self.SUFFIX_SELECTED = '正在加载请稍后...'
        self.display()
        self.start = 0
        while True:  # 无红心兆赫进入下一个频道
            try:
                self.douban.set_channel(self.douban.channels[self.markline]['channel_id'])  # 设置默认频率
                self.douban.get_playlist()
                self.play()
                break
            except:
                self.markline += 1
                self.displayline += 1
        self.thread(self.run)

    def thread(self,target):
        threading.Thread(target=target).start()

    # 获取config
    def get_config(self):
        config = ConfigParser.ConfigParser()
        with open(os.path.expanduser('~/.doubanfm_config'), 'r') as cfgfile:
            config.readfp(cfgfile)
            options = config.options('key')
            for option in options:
                option = option.upper()
                if self.KEYS.has_key(option):
                    self.KEYS[option] = config.get('key', option)

    # 歌词线程
    def display_lrc(self):
        while self.lrc_display:
            self.lrc_dict = self.douban.get_lrc()
            if self.lrc_dict:
                Lrc(self.lrc_dict, self)
            else:
                self.lrc_display = 0

    # 显示时间,音量的线程
    def display_time(self):
        length = len(self.TITLE)
        while True:
            if self.q == 1:  # 退出
                break
            if self.song_time >= 0 and self.douban.playingsong:
                minute = int(self.song_time) / 60
                sec = int(self.song_time) % 60
                show_time = str(minute).zfill(2) + ':' + str(sec).zfill(2)

                self.volume = self.get_volume()  # 获取音量
                self.TITLE = self.TITLE[:length - 1] + '  ' + self.douban.playingsong['kbps'] + 'kbps  ' + colored(show_time, 'cyan') + '  rate: ' + colored(self.rate[int(round(self.douban.playingsong['rating_avg'])) - 1], 'red') + '  vol: '
                if self.is_muted:
                    self.TITLE += '✖'
                else:
                    self.TITLE += self.volume.strip() + '%'
                if self.loop:
                    self.TITLE += '  ' + colored('↺', 'red')
                else:
                    self.TITLE += '  ' + colored('→', 'red')
                self.TITLE += '\r'
                self.display()
                if not self.pause:
                    self.song_time -= 1
            else:
                self.TITLE = self.TITLE[:length]
            time.sleep(1)

    # 增加一个歌词界面的判断
    def display(self):
        if not self.lrc_display and self.start and not self.lock_help:
            cli.Cli.display(self)

    # 获取音量
    def get_volume(self):
        if self.platform == 'Linux':
            volume = subprocess.check_output('amixer get Master | grep Mono: | cut -d " " -f 6', shell=True)
            return volume[1:-3]
        elif self.platform == 'Darwin':
            return subprocess.check_output('osascript -e "output volume of (get volume settings)"', shell=True)
        else:
            return

    # 调整音量大小
    def change_volume(self, increment):
        if increment == 1:
            volume = int(self.volume) + 5
        else:
            volume = int(self.volume) - 5
        if self.platform == 'Linux':
            subprocess.Popen('amixer set Master ' + str(volume) + '% >/dev/null 2>&1', shell=True)
        elif self.platform == 'Darwin':
            subprocess.Popen('osascript -e "set volume output volume ' + str(volume) + '"', shell=True)
        else:
            pass

    # 静音
    def mute(self):
        if self.is_muted:
            self.is_muted = False
            mute = 0
        else:
            self.is_muted = True
            mute = 1
        subprocess.Popen('echo "mute {mute}" > {fifo}'.format(fifo=self.mplayer_controller, mute=mute), shell=True, stdin=subprocess.PIPE)

    # 守护线程,检查歌曲是否播放完毕
    def protect(self):
        while True:
            if self.q == 1:
                break
            if self.start:
                self.p.poll()
                if self.p.returncode == 0:
                    self.song_time = -1
                    if not self.loop and self.douban.playingsong:
                        self.douban.end_music()  # 发送完成
                    self.play()
            time.sleep(1)

    # 播放歌曲
    def play(self):
        self.lrc_dict = {}  # 歌词清空
        if not self.loop:
            self.douban.get_song()
        if self.is_muted:  # 静音状态
            subprocess.Popen('echo "mute {mute}" > {fifo}'.format(fifo=self.mplayer_controller, mute=1), shell=True, stdin=subprocess.PIPE)
        song = self.douban.playingsong
        self.song_time = song['length']
        # 是否是红心歌曲
        if song['like'] == 1:
            love = self.love
        else:
            love = ''
        title = colored(song['title'], 'green')
        albumtitle = colored(song['albumtitle'], 'yellow')
        artist = colored(song['artist'], 'white')
        self.SUFFIX_SELECTED = (love + ' ' + title + ' • ' + albumtitle + ' • ' + artist + ' ' + song['public_time']).replace('\\', '')

        cmd = 'mplayer -slave -input file={fifo} {song_url} >/dev/null 2>&1'
        self.p = subprocess.Popen(cmd.format(fifo=self.mplayer_controller, song_url=song['url']), shell=True, stdin=subprocess.PIPE)  # subprocess.PIPE防止继承父进程
        self.pause = False
        self.display()
        self.notifySend()
        if self.lrc_display:  # 获取歌词
            self.lrc_dict = self.douban.get_lrc()
            if not self.lrc_dict:  # 歌词获取失败,关闭歌词界面
                self.lrc_display = 0
        self.start = 1

    # 暂停歌曲
    def pause_play(self):
        subprocess.Popen('echo "pause" > {fifo}'.format(fifo=self.mplayer_controller), shell=True, stdin=subprocess.PIPE)
        if self.pause:
            self.pause = False
            self.notifySend(content='开始播放')
        else:
            self.notifySend(content='暂停播放')
            self.pause = True

    # 结束mplayer
    def kill_mplayer(self):
        subprocess.Popen('echo "quit" > {fifo}'.format(fifo=self.mplayer_controller), shell=True, stdin=subprocess.PIPE)

    # 发送桌面通知
    def notifySend(self, title=None, content=None, path=None):
        if not title and not content:
            title = self.douban.playingsong['title']
        elif not title:
            title = self.douban.playingsong['title'] + ' - ' + self.douban.playingsong['artist']
        if not path:
            path = self.douban.get_pic()  # 获取封面
        if not content:
            content = self.douban.playingsong['artist']

        try:
            if self.platform == 'Linux':
                self.send_Linux_notify(title, content, path)
            elif self.platform == 'Darwin':
                self.send_OS_X_notify(title, content, path)
        except:
            pass

    def send_Linux_notify(self, title, content, img_path):
        subprocess.call(['notify-send', '-i', img_path, title, content])

    def send_OS_X_notify(self, title, content, img_path):
        NSUserNotification = objc.lookUpClass('NSUserNotification')
        NSUserNotificationCenter = objc.lookUpClass('NSUserNotificationCenter')
        NSImage = objc.lookUpClass('NSImage')
        notification = NSUserNotification.alloc().init()
        notification.setTitle_(title.decode('utf-8'))
        notification.setSubtitle_('')
        notification.setInformativeText_(content.decode('utf-8'))
        notification.setUserInfo_({})
        image = NSImage.alloc().initWithContentsOfFile_(img_path)
        notification.setContentImage_(image)
        notification.setSoundName_("NSUserNotificationDefaultSoundName")
        notification.setDeliveryDate_(Foundation.NSDate.dateWithTimeInterval_sinceDate_(0, Foundation.NSDate.date()))
        NSUserNotificationCenter.defaultUserNotificationCenter().scheduleNotification_(notification)

    def run(self):
        while True:
            self.display()
            c = getch._Getch()()
            if self.lrc_display or self.lock_help:  # 歌词界面截断
                if c == self.KEYS['QUIT']:
                    self.lrc_display = 0
                    self.lock_help = 0
                continue
            if c == self.KEYS['UP']:
                self.updown(-1)
            elif c == self.KEYS['DOWN']:
                self.updown(1)
            elif c == '1':
                Help(self)
            elif c == self.KEYS['LRC']:  # o歌词
                self.set_lrc()
                self.thread(self.display_lrc)
            elif c == self.KEYS['RATE']:  # r标记红心/取消标记
                self.thread(self.set_rate)
            elif c == self.KEYS['NEXT']:  # n下一首
                self.set_next()
            elif c == self.KEYS['TOP']:  # g键返回顶部
                self.markline = 0
                self.topline = 0
            elif c == self.KEYS['BOTTOM']:  # G键返回底部
                self.markline = self.screenline
                self.topline = len(self.lines) - self.screenline - 1
            elif c == ' ':  # 空格选择频道,播放歌曲
                if self.markline + self.topline != self.displayline:
                    self.displaysong()
                    self.set_play()
            elif c == self.KEYS['OPENURL']:  # l打开当前播放歌曲豆瓣页
                self.set_url()
            elif c == self.KEYS['BYE']:  # b不再播放
                self.set_bye()
            elif c == self.KEYS['PAUSE']:  # p暂停
                self.pause_play()
            elif c == self.KEYS['MUTE']:  # m静音
                self.mute()
            elif c == self.KEYS['LOOP']:  # l单曲循环
                self.set_loop()
            elif c == self.KEYS['QUIT']:  # q退出程序
                self.set_quit()
            elif c == '=':
                self.change_volume(1)
            elif c == '-':
                self.change_volume(-1)


    def info(args):
        """
        装饰器,用来改变SUFFIX_SELECTED并在界面输出
        """
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
        """
        歌曲加心，去心
        """
        while(self.lock_rate):
            if self.q == 1:
                return
        self.lock_rate = 1
        if self.douban.playingsong:
            if not self.douban.playingsong['like']:
                self.SUFFIX_SELECTED = self.love + self.SUFFIX_SELECTED
                self.display()
                self.douban.rate_music()
                self.douban.playingsong['like'] = 1
                self.notifySend(content='标记红心')
            else:
                self.SUFFIX_SELECTED = self.SUFFIX_SELECTED[len(self.love):]
                self.display()
                self.douban.unrate_music()
                self.douban.playingsong['like'] = 0
                self.notifySend(content='取消标记红心')
        self.lock_rate = 0

    def set_loop(self):
        if self.loop:
            self.notifySend(content='停止单曲循环')
            self.loop = False
        else:
            self.notifySend(content='单曲循环')
            self.loop = True

    def set_url(self):
        import webbrowser
        url = "http://music.douban.com" + self.douban.playingsong['album'].replace('\/', '/')
        webbrowser.open(url)
        self.display()

    def set_quit(self):
        self.q = 1
        if self.start:
            self.kill_mplayer()
        subprocess.call('echo -e "\033[?25h";clear', shell=True)
        exit()

    @info('正在加载请稍后...')
    def set_play(self):
        self.start = 0
        if self.douban.playingsong:
            self.douban.playingsong = {}
            self.kill_mplayer()
        self.douban.set_channel(self.douban.channels[self.markline + self.topline]['channel_id'])
        self.douban.get_playlist()
        self.play()

    @info('正在加载请稍后...')
    def set_next(self):
        if self.douban.playingsong:
            self.loop = False
            self.start = 0
            self.kill_mplayer()
            self.thread(self.douban.skip_song)  # 线程处理网络请求
            self.douban.playingsong = {}
            self.play()

    @info('不再播放,切换下一首...')
    def set_bye(self):
        if self.douban.playingsong:
            self.start = 0  # 每个play前需self.start置0
            self.kill_mplayer()
            self.douban.bye()
            self.douban.playingsong = {}
            self.play()

    @info('正在查找歌词...')
    def set_lrc(self):
        self.lrc_display = 1

class Lrc(cli.Cli):
    def __init__(self, lrc_dict, win):
        self.win = win
        self.lrc_dict = lrc_dict

        self.length = int(win.douban.playingsong['length'])  # 歌曲总长度
        self.song_time = self.length - win.song_time - 1  # 歌曲播放秒数

        self.screenline_char = win.screenline_char  # shell每行字符数,居中用
        self.screenline = win.screenline  # shell高度

        self.sort_lrc_dict = sorted(lrc_dict.iteritems(), key=lambda x: x[0])
        self.lines = [line[1] for line in self.sort_lrc_dict if line[1]]

        subprocess.call('clear', shell=True) # 清屏

        self.markline = self.find_line()
        self.topline = 0
        self.display()
        self.display_line()

    # 第一次载入时查找歌词
    def find_line(self):
        for time in reversed(range(self.song_time)):
            locate = [index for index, i in enumerate(self.sort_lrc_dict) if i[0] == time]  # 查找歌词在self.sort_lrc_dict中的位置
            if locate:
                return locate[0]
        return 0

    # 显示歌词
    def display_line(self):
        while self.win.lrc_display:
            self.display()
            if self.song_time < self.length:
                self.song_time += 1
                locate = [index for index, i in enumerate(self.sort_lrc_dict) if i[0] == self.song_time]  # 查找歌词在self.sort_lrc_dict中的位置
                if locate:
                    self.markline = locate[0]
                    self.display()
                time.sleep(1)
            else:
                break

    # 中文字符
    def is_cn_char(self, i):
            return 0x4e00<=ord(i)<0x9fa6

    # 输出界面
    def display(self):
        subprocess.call('clear', shell=True)
        print
        print self.win.TITLE
        print
        for linenum in range(self.screenline - 2):
            if self.screenline/2 - linenum > self.markline - self.topline or linenum - self.screenline/2 >= len(self.lines) - self.markline:
                print
            else:
                line = self.lines[self.markline - (self.screenline/2 - linenum)].strip()
                l = self.center_num(line)
                flag_num = (self.screenline_char - l) / 2
                if linenum == self.screenline/2:
                    i = colored(line, 'blue')
                    print ' ' * flag_num + i + '\r'
                else:
                    print ' ' * flag_num + line + '\r'
        print
        # 歌曲信息居中
        song = self.win.douban.playingsong
        tmp = (song['title'] + song['albumtitle'] + song['artist'] + song['public_time']).replace('\\', '').strip()
        tmp = unicode(tmp, 'utf-8')
        l = self.center_num(tmp) + 7  # 7个固定字符
        if song['like']:
            l += 2
        flag_num = (self.screenline_char - l) / 2
        print ' ' * flag_num + self.win.SUFFIX_SELECTED + '\r'

    # 需要考虑中文和英文的居中
    def center_num(self, tmp):
        l = 0
        for i in tmp:
            if self.is_cn_char(i):
                l += 2
            else:
                l += 1
        return l

class Help(cli.Cli):
    def __init__(self, win):
        self.win = win
        self.win.lock_help = 1
        self.win.thread(self.display_help)

    def display_help(self):
        while self.win.lock_help:
            self.display()
            time.sleep(1)
        self.win.lock_help = 0

    def display(self):
        subprocess.call('clear', shell=True)
        print
        print self.win.TITLE
        print
        print "haha"

def main():
    douban = douban_token.Doubanfm()
    Win(douban)

if __name__ == '__main__':
    main()

############################################################################
