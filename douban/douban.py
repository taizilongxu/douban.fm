#!/usr/bin/env python
#-*- encoding: UTF-8 -*-
"""
豆瓣FM主程序
"""
#---------------------------------import------------------------------------
import cli
import douban_token
import getch
import subprocess
from termcolor import colored
import threading
import string
import time
import os
import urllib2
#---------------------------------------------------------------------------
douban = douban_token.Doubanfm()

class Win(cli.Cli):

    def __init__(self, lines):
        if douban.pro == 0:
            PRO = ''
        else:
            PRO = colored(' PRO ', attrs = ['reverse'])
        self.TITLE += douban.user_name + ' ' + PRO + ' ' + ' >>\r'
        self.start = 0 # 歌曲播放
        self.q = 0 # 退出
        self.song_time = -1 # 歌曲剩余播放时间
        self.rate = ['★ '*i for i in range(1,6)] # 歌曲评分
        # 守护线程
        self.t = threading.Thread(target=self.protect)
        self.t.start()
        self.t2 = threading.Thread(target=self.display_time)
        self.t2.start()
        super(Win, self).__init__(lines)
        # 启动自动播放
        self.SUFFIX_SELECTED = '正在加载请稍后...'
        self.display()
        douban.set_channel(douban.channels[self.markline]['channel_id']) # 设置默认频率
        douban.get_playlist()
        self.play()
        self.start = 1
        self.run()

    # 显示时间的线程
    def display_time(self):
        length = len(self.TITLE)
        while True:
            if self.q == 1:
                break
            if self.song_time >= 0 and douban.playingsong:
                minute = int(self.song_time) / 60
                sec = int(self.song_time) % 60
                show_time = string.zfill(str(minute), 2) + ':' + string.zfill(str(sec), 2)
                self.TITLE = self.TITLE[:length - 1] + '  ' + douban.playingsong['kbps'] + 'kbps  ' + colored(show_time, 'cyan') + '  rate: ' + colored(self.rate[int(round(douban.playingsong['rating_avg'])) - 1], 'red') + '\r'
                self.display()
                self.song_time -= 1
            else:
                self.TITLE = self.TITLE[:length]
            time.sleep(1)

    # 守护线程,检查歌曲是否播放完毕
    def protect(self):
        while True:
            if self.q == 1:
                break
            if self.start:
                self.p.poll()
                if self.p.returncode == 0:
                    self.song_time = -1
                    douban.end_music()
                    self.play()
            time.sleep(1)

    # 播放歌曲
    def play(self):
        douban.get_song()
        song = douban.playingsong
        self.song_time = song['length']
        # 是否是红心歌曲
        if song['like'] == 1:
            love = self.love
        else:
            love = ''
        self.SUFFIX_SELECTED = love + colored(song['title'], 'green') + ' • ' + colored(song['albumtitle'], 'yellow') + ' • ' + colored(song['artist'], 'white') + ' ' + song['public_time']

        self.p = subprocess.Popen('mplayer ' + song['url'] + ' -slave  >/dev/null 2>&1', shell=True, stdin=subprocess.PIPE) # subprocess.PIPE防止继承父进程
        self.display()
        self.notifySend()

    # 结束mplayer
    def kill_mplayer(self):
        if subprocess.check_output('ps -a | grep mplayer', shell=True):
            subprocess.Popen('killall -9 mplayer', shell=True)

    def downloadPic(self, path, name, url):
        with open(path + name, 'w') as pic:
            pic.write(urllib2.urlopen(url).read())

    # 发送桌面通知
    def notifySend(self):
        picture = douban.playingsong['picture']

        # get icon
        name = picture[picture.rindex(os.sep)+1:]
        # /home/xxx/douban.fm works, .. does not work
        songpath = os.path.abspath(os.path.pardir) + os.sep + 'songpics' + os.sep
        url =  picture.replace('\\','')
        if not os.path.exists(songpath + name):
            self.downloadPic(songpath, name, url)

        title = douban.playingsong['title']
        content = douban.playingsong['artist']
        subprocess.call([ 'notify-send', '-i',  songpath + name, title, content])

    def run(self):
        while True:
            self.display()
            i = getch._Getch()
            c = i()
            if c == 'k':
                self.updown(-1)
            elif c == 'j':
                self.updown(1)
            elif c == 'g': # g键返回顶部
                self.markline = 0
                self.topline = 0
            elif c == "G": # G键返回底部
                self.markline = self.screenline
                self.topline = len(self.lines) - self.screenline - 1
            elif c == ' ': # 空格选择频道,播放歌曲
                if self.markline + self.topline != self.displayline:
                    if douban.playingsong:
                        douban.playingsong = {}
                        self.kill_mplayer()
                    self.displaysong()
                    self.SUFFIX_SELECTED = '正在加载请稍后...'
                    self.display()
                    douban.set_channel(douban.channels[self.markline + self.topline]['channel_id'])
                    douban.get_playlist()
                    self.play()
                    self.start = 1
            elif c == 'l': # l打开当前播放歌曲豆瓣页
                import webbrowser
                webbrowser.open("http://music.douban.com" + douban.playingsong['album'])
                self.display()
            elif c == 'r': # r标记红心/取消标记
                if douban.playingsong:
                    if not douban.playingsong['like']:
                        self.SUFFIX_SELECTED = self.love + self.SUFFIX_SELECTED
                        self.display()
                        douban.rate_music()
                        douban.playingsong['like'] = 1
                    else:
                        self.SUFFIX_SELECTED = self.SUFFIX_SELECTED[len(self.love):]
                        self.display()
                        douban.unrate_music()
                        douban.playingsong['like'] = 0
            elif c =='n': # n下一首
                if douban.playingsong:
                    self.kill_mplayer()
                    self.SUFFIX_SELECTED = '正在加载请稍后...'
                    self.display()
                    douban.skip_song()
                    douban.playingsong = {}
                    self.play()
            elif c =='b': # b不再播放
                if douban.playingsong:
                    self.kill_mplayer()
                    douban.bye()
                    self.play()
            elif c == 'q':
                self.q = 1
                if self.start:
                    self.kill_mplayer()
                subprocess.call('echo -e "\033[?25h";clear', shell=True)
                exit()

def main():
    w = Win(douban.lines)

if __name__ == '__main__':
    main()
############################################################################
