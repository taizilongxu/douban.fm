
#!/usr/bin/env python2
# -*- coding: utf-8 -*-
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

    # def __del__(self):
    #     self.win.state = 0

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
                    i = color_func(self.c['LRC']['highlight'])(line)
                    print ' ' * flag_num + i + '\r'
                else:
                    line = color_func(self.c['LRC']['line'])(line)
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
        l = self.center_num(tmp)
        if song['like']:
            l += 2
        flag_num = (self.screen_width - l) / 2
        self.title = ' ' * flag_num + self.win.SUFFIX_SELECTED + '\r'  # 歌词页面标题
        print self.title
