#-*- encoding: UTF-8 -*-
#---------------------------------import------------------------------------
import cli
import douban_token
import getch
import subprocess
from termcolor import colored
#---------------------------------------------------------------------------
douban = douban_token.Doubanfm()

lines = []
def get_channellines():
    for index,channel in enumerate(douban.channels):
        lines.append(channel['name'])
    return lines

lines = get_channellines()

class Win(cli.Cli):
    def __init__(self, lines):
        self.TITLE += douban.user_name + ' >'
        super(Win, self).__init__(lines)

    def run(self):
        while True:
            self.display()
            i = getch._Getch()
            c = i()
            if c == 'k':
                self.updown(-1)
            elif c == 'j':
                self.updown(1)
            elif c == ' ':
                '选择频道,播放歌曲'
                if self.markline + self.topline != self.displayline:
                    self.displaysong()
                    self.SUFFIX_SELECTED = '正在加载请稍后...'
                    self.display()
                    douban.set_channel(douban.channels[self.markline + self.topline]['channel_id'])
                    douban.get_playlist()
                    douban.get_song()
                    song = douban.playingsong
                    '是否是红心歌曲'
                    if song['like'] == 1:
                        love = self.love
                    else:
                        love = ''
                    self.SUFFIX_SELECTED = love + colored(song['title'], 'green') + ' ' + song['kbps'] + 'kbps ' + colored(song['albumtitle'], 'yellow') + ' • ' + colored(song['artist'], 'white') + ' ' + song['public_time']
                    self.display()
                    # subprocess.Popen('mplayer ' + song['url'] + ' >/dev/null 2>&1', shell=True)
            elif c == 'r':
                '标记红心,取消标记'
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
            elif c =='n':
                '下一首'
                self.SUFFIX_SELECTED = '正在加载请稍后...'
                self.display()
                douban.get_song()
                song = douban.playingsong
                '是否是红心歌曲'
                if song['like'] == 1:
                    love = self.love
                else:
                    love = ''
                self.SUFFIX_SELECTED = love + colored(song['title'], 'green') + ' ' + song['kbps'] + 'kbps ' + colored(song['albumtitle'], 'yellow') + ' • ' + colored(song['artist'], 'white') + ' ' + song['public_time']
                self.display()
                # subprocess.Popen('killall -9 mplayer', shell=True)
                # subprocess.Popen('mplayer' + song['url'] + '>dev/null 2>&1', shell=True)
            elif c == 'q':
                exit()

w = Win(lines)
############################################################################
