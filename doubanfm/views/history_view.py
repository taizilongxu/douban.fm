
#!/usr/bin/env python2
# -*- coding: utf-8 -*-
class History(cli.Cli):
    '''历史记录'''
    def __init__(self, win):
        self.win = win
        self.KEYS = self.win.KEYS
        # the playlist of the history
        self.screen_height, self.screen_width = self.linesnum()

        # 3个tab, playlist history rate
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
                line = color_func(self.c['PLAYINGSONG']['title'])(line)
                line = str(index) + ' ' + line
                if i['like'] == 1:
                    line += self.LOVE
                if i == self.win.playingsong:
                    line += self.play_tag
                self.lines.append(line)
        elif self.state == 1:
            # 历史列表
            for index, i in enumerate(self.win.history):
                line = i['title'] if len(i['title']) < width else i['title'][:width]
                line = color_func(self.c['PLAYINGSONG']['title'])(line)
                line = i['time'][5:] + ' ' + line
                if i['like'] == 1:
                    line += self.LOVE
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
                line = color_func(self.c['PLAYINGSONG']['title'])(line)
                line = str(index) + ' ' + line + self.LOVE
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
            if c == self.KEYS['UP'] or c == 'A' and self.markline != 1:
                self.updown(-1)
            elif c == self.KEYS['DOWN'] or c == 'B':
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
            elif c == 'h' or c == 'D':
                self.state -= 1 if self.state != 0 else -2
                self.get_lines()
            elif c == 'l' or c == 'C':
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
