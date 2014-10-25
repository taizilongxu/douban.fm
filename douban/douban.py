#!/usr/bin/env python
#-*- encoding: UTF-8 -*-
"""
豆瓣FM主程序
"""
#---------------------------------import------------------------------------
import cli # UI
import douban_token # network
import getch # get char
import subprocess
from termcolor import colored
import threading
import string
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
        self.platform = platform.system()
        self.get_config()
        self.douban = douban
        if self.douban.pro == 0:
            PRO = ''
        else:
            PRO = colored(' PRO ', attrs = ['reverse'])
        self.TITLE += self.douban.user_name + ' ' + PRO + ' ' + ' >>\r'
        self.start = 0 # 歌曲播放
        self.q = 0 # 退出
        self.lrc_dict = {} # 歌词
        self.song_time = -1 # 歌曲剩余播放时间
        self.rate = ['★ '*i for i in range(1,6)] # 歌曲评分
        self.lrc_display = 0 # 是否显示歌词
        self.pause = True
        self.mplayer_controller = os.path.join(tempfile.mkdtemp(), 'mplayer_controller')
        self.loop = False
        self.is_muted = False # 是否静音
        os.mkfifo(self.mplayer_controller)
        # 守护线程
        self.t1 = threading.Thread(target=self.protect)
        self.t2 = threading.Thread(target=self.display_time)
        self.t3 = threading.Thread(target=self.display_lrc)
        self.t1.start()
        self.t2.start()
        self.t3.start()
        super(Win, self).__init__(self.douban.lines)
        # 启动自动播放
        self.SUFFIX_SELECTED = '正在加载请稍后...'
        self.display()
        self.douban.set_channel(self.douban.channels[self.markline]['channel_id']) # 设置默认频率
        self.douban.get_playlist()
        self.play()
        self.start = 1
        self.run()

    # 获取config
    def get_config(self):
        config=ConfigParser.ConfigParser()
        with open(os.path.expanduser('~/.doubanfm_config'),'r') as cfgfile:
            config.readfp(cfgfile)
            self.UP = config.get('key','UP')
            self.DOWN = config.get('key','DOWN')
            self.TOP = config.get('key','TOP')
            self.BOTTOM = config.get('key','BOTTOM')
            self.OPENURL = config.get('key','OPENURL')
            self.RATE = config.get('key','RATE')
            self.NEXT = config.get('key','NEXT')
            self.BYE = config.get('key','BYE')
            self.QUIT = config.get('key','QUIT')
            self.PAUSE = config.get('key', 'PAUSE')
            self.LOOP = config.get('key', 'LOOP')
            self.MUTE = config.get('key', 'MUTE')

    # 歌词线程
    def display_lrc(self):
        while True:
            if self.q == 1: # 退出
                break
            if self.lrc_display and self.lrc_dict:
                lrc_cli = Lrc(self.lrc_dict, self)
            time.sleep(1)

    # 显示时间,音量的线程
    def display_time(self):
        length = len(self.TITLE)
        while True:
            if self.q == 1:
                break
            if self.song_time >= 0 and self.douban.playingsong:
                minute = int(self.song_time) / 60
                sec = int(self.song_time) % 60
                show_time = string.zfill(str(minute), 2) + ':' + string.zfill(str(sec), 2)
                self.get_volume() # 获取音量
                self.TITLE = self.TITLE[:length - 1] + '  ' + self.douban.playingsong['kbps'] + 'kbps  ' + colored(show_time, 'cyan') + '  rate: ' + colored(self.rate[int(round(self.douban.playingsong['rating_avg'])) - 1], 'red') + '  vol: '
                if self.is_muted:
                    self.TITLE += '✖'
                else:
                    self.TITLE += self.volume.strip() + '%'
                if self.loop:
                    self.TITLE += '  ' + colored('◎', 'red')
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
        if not self.lrc_display:
            cli.Cli.display(self)

    # 获取音量
    def get_volume(self):
        if self.platform == 'Linux':
            volume = subprocess.check_output('amixer get Master | grep Mono: | cut -d " " -f 6', shell=True)
            volume = volume[1:-3]
        elif self.platform == 'Darwin':
            volume = subprocess.check_output('osascript -e "output volume of (get volume settings)"', shell=True)
        else:
            volume = ''
        self.volume = volume

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
                    if not self.loop:
                        self.douban.end_music()
                    self.play()
            time.sleep(1)

    # 播放歌曲
    def play(self):
        self.lrc_dict = {} # 歌词清空
        if not self.loop:
            self.douban.get_song()
        song = self.douban.playingsong
        self.song_time = song['length']
        # 是否是红心歌曲
        if song['like'] == 1:
            love = self.love
        else:
            love = ''
        self.SUFFIX_SELECTED = (love + colored(song['title'], 'green') + ' • ' + colored(song['albumtitle'], 'yellow') + ' • ' + colored(song['artist'], 'white') + ' ' + song['public_time']).replace('\\', '')

        cmd = 'mplayer -slave -input file={fifo} {song_url} >/dev/null 2>&1'
        self.p = subprocess.Popen(cmd.format(fifo=self.mplayer_controller, song_url=song['url']), shell=True, stdin=subprocess.PIPE) # subprocess.PIPE防止继承父进程
        self.pause = False
        self.display()
        self.notifySend()
        if self.lrc_display: # 获取歌词
            self.lrc_dict = self.douban.get_lrc()
            if not self.lrc_dict: # 歌词获取失败,关闭歌词界面
                self.lrc_display = 0

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
            path = self.douban.get_pic() # 获取封面
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
        subprocess.call([ 'notify-send', '-i', img_path, title, content])

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
            i = getch._Getch()
            c = i()
            if self.lrc_display:
                if c == self.QUIT:
                    self.lrc_display = 0
                    continue
                else:
                    continue
            if c == self.UP:
                self.updown(-1)
            elif c == self.DOWN:
                self.updown(1)
            elif c == self.TOP: # g键返回顶部
                self.markline = 0
                self.topline = 0
            elif c == self.BOTTOM: # G键返回底部
                self.markline = self.screenline
                self.topline = len(self.lines) - self.screenline - 1
            elif c == ' ': # 空格选择频道,播放歌曲
                if self.markline + self.topline != self.displayline:
                    if self.douban.playingsong:
                        self.douban.playingsong = {}
                        self.kill_mplayer()
                    self.displaysong()
                    self.SUFFIX_SELECTED = '正在加载请稍后...'
                    self.display()
                    self.douban.set_channel(self.douban.channels[self.markline + self.topline]['channel_id'])
                    self.douban.get_playlist()
                    self.play()
                    self.start = 1
            elif c == self.OPENURL: # l打开当前播放歌曲豆瓣页
                import webbrowser
                webbrowser.open("http://music.douban.com" + self.douban.playingsong['album'].replace('\/', '/'))
                self.display()
            elif c == self.RATE: # r标记红心/取消标记
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
            elif c == self.NEXT: # n下一首
                if self.douban.playingsong:
                    self.kill_mplayer()
                    self.SUFFIX_SELECTED = '正在加载请稍后...'
                    self.display()
                    self.douban.skip_song()
                    self.douban.playingsong = {}
                    self.play()
            elif c == self.BYE: # b不再播放
                if self.douban.playingsong:
                    self.SUFFIX_SELECTED = '不再播放,切换下一首...'
                    self.display()
                    self.kill_mplayer()
                    self.douban.bye()
                    self.play()
            elif c == self.PAUSE:
                self.pause_play()
            elif c == self.MUTE:
                self.mute()
            elif c == self.LOOP:
                if self.loop:
                    self.notifySend(content='停止单曲循环')
                    self.loop = False
                else:
                    self.notifySend(content='单曲循环')
                    self.loop = True
            elif c == self.QUIT:
                self.q = 1
                if self.start:
                    self.kill_mplayer()
                subprocess.call('echo -e "\033[?25h";clear', shell=True)
                exit()
            elif c == '=':
                self.change_volume(1)
            elif c == '-':
                self.change_volume(-1)
            elif c == 'o':
                tmp = self.SUFFIX_SELECTED
                self.SUFFIX_SELECTED = '正在加载歌词'
                self.display()
                self.lrc_display = 1
                self.SUFFIX_SELECTED = tmp
                self.lrc_dict = self.douban.get_lrc()
                if self.lrc_dict:
                    self.lrc_display = 1
                else:
                    self.lrc_display = 0

class Lrc(cli.Cli):
    def __init__(self, lrc_dict, win):
        self.win = win
        self.lrc_dict = lrc_dict
        self.length = int(win.douban.playingsong['length']) # 歌曲总长度
        self.song_time = self.length - win.song_time - 1 # 歌曲播放秒数
        self.screenline_char = win.screenline_char # shell每行字符数,居中用
        self.sort_lrc_dict = sorted(lrc_dict.iteritems(), key=lambda x : x[0])
        lrc_lines = [line[1] for line in self.sort_lrc_dict if line[1]]
        self.lines = lrc_lines
        self.screenline = win.screenline
        subprocess.call('clear', shell=True)

        self.markline = 0
        self.topline = 0
        self.q = 0
        self.display()
        self.display_line()

    # 显示歌词
    def display_line(self):
        while True:
            if not self.win.lrc_display:
                break
            self.display()
            if self.song_time < self.length:
                self.song_time += 1
                s = [index for index,i in enumerate(self.sort_lrc_dict) if i[0] == self.song_time] # 查找歌词在self.sort_lrc_dict中的位置
                if s:
                    self.markline = s[0]
                    self.display()
                time.sleep(1)
            else:
                break
    # 输出界面
    def display(self):
        subprocess.call('clear', shell=True)
        print
        print self.win.TITLE
        top = self.topline
        bottom = self.topline + self.screenline + 1
        for linenum in range(self.screenline):
            if self.screenline/2 - linenum > self.markline - self.topline or linenum - self.screenline/2 >= len(self.lines) - self.markline:
                print
            else:
                line = self.lines[self.markline - (self.screenline/2 - linenum)]
                if linenum == self.screenline/2:
                    i = colored(line, 'blue')
                    print i.center(self.screenline_char - 1) + '\r'
                else:
                    print line.center(self.screenline_char - 9) + '\r'

def main():
    douban = douban_token.Doubanfm()
    w = Win(douban)

if __name__ == '__main__':
    main()

############################################################################
