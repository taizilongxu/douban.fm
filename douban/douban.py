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
import ConfigParser
#---------------------------------------------------------------------------
class Win(cli.Cli):

    def __init__(self, douban):
        self.get_config()
        self.douban = douban
        if self.douban.pro == 0:
            PRO = ''
        else:
            PRO = colored(' PRO ', attrs = ['reverse'])
        self.TITLE += self.douban.user_name + ' ' + PRO + ' ' + ' >>\r'
        self.start = 0 # 歌曲播放
        self.q = 0 # 退出
        self.song_time = -1 # 歌曲剩余播放时间
        self.rate = ['★ '*i for i in range(1,6)] # 歌曲评分
        # 守护线程
        self.t = threading.Thread(target=self.protect)
        self.t2 = threading.Thread(target=self.display_time)
        self.t.start()
        self.t2.start()
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
                self.TITLE = self.TITLE[:length - 1] + '  ' + self.douban.playingsong['kbps'] + 'kbps  ' + colored(show_time, 'cyan') + '  rate: ' + colored(self.rate[int(round(self.douban.playingsong['rating_avg'])) - 1], 'red') + ' ' + self.volume.strip() + '%' + '\r'
                self.display()
                self.song_time -= 1
            else:
                self.TITLE = self.TITLE[:length]
            time.sleep(1)

    # 获取音量
    def get_volume(self):
        volume = subprocess.check_output('amixer get Master | grep Mono: | cut -d " " -f 6', shell=True)
        self.volume = volume[1:-3]

    # 调整音量大小
    def change_volume(self, increment):
        if increment == 1:
            volume = int(self.volume) + 5
        else:
            volume = int(self.volume) - 5
        subprocess.Popen('amixer set Master ' + str(volume) + '% >/dev/null 2>&1', shell=True)

    # 守护线程,检查歌曲是否播放完毕
    def protect(self):
        while True:
            if self.q == 1:
                break
            if self.start:
                self.p.poll()
                if self.p.returncode == 0:
                    self.song_time = -1
                    self.douban.end_music()
                    self.play()
            time.sleep(1)

    # 播放歌曲
    def play(self):
        self.douban.get_song()
        song = self.douban.playingsong
        self.song_time = song['length']
        # 是否是红心歌曲
        if song['like'] == 1:
            love = self.love
        else:
            love = ''
        self.SUFFIX_SELECTED = (love + colored(song['title'], 'green') + ' • ' + colored(song['albumtitle'], 'yellow') + ' • ' + colored(song['artist'], 'white') + ' ' + song['public_time']).replace('\\', '')

        self.p = subprocess.Popen('mplayer ' + song['url'] + ' -slave  >/dev/null 2>&1', shell=True, stdin=subprocess.PIPE) # subprocess.PIPE防止继承父进程
        self.display()
        self.notifySend()

    # 结束mplayer
    def kill_mplayer(self):
        if subprocess.check_output('ps -a | grep mplayer', shell=True):
            subprocess.Popen('killall -9 mplayer >/dev/null 2>&1', shell=True)

    # 发送桌面通知
    def notifySend(self):
        self.douban.get_pic() # 获取封面
        path = os.path.abspath('.') + os.sep + 'tmp.jpg'
        title = self.douban.playingsong['title']
        content = self.douban.playingsong['artist']
        subprocess.call([ 'notify-send', '-i', path, title, content])
        os.remove(path) # 删除图片

    def run(self):
        while True:
            self.display()
            i = getch._Getch()
            c = i()
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
                    else:
                        self.SUFFIX_SELECTED = self.SUFFIX_SELECTED[len(self.love):]
                        self.display()
                        self.douban.unrate_music()
                        self.douban.playingsong['like'] = 0
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
                    self.kill_mplayer()
                    self.douban.bye()
                    self.play()
            elif c == self.QUIT:
                self.q = 1
                if self.start:
                    self.kill_mplayer()
                subprocess.call('echo -e "\033[?25h";clear', shell=True)
                exit()
            elif c == '=': # 音量+
                self.change_volume(1)
            elif c == '-': # 音量-
                self.change_volume(-1)

def main():
    douban = douban_token.Doubanfm()
    w = Win(douban)

if __name__ == '__main__':
    main()
############################################################################
