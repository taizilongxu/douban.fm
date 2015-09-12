#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
处理main_view的数据

control和view中间层, 负责生成显示的内容(增加主题色彩)

    dal = MainDal(playingsong, play_state, config)

    dal.title
    dal.love
    dal.prefix_selected
    dal.prefix_deselected
    dal.suffix_selected
    dal.suffix_deselected
"""
from config import db_config
from colorset.colors import on_light_red, color_func  # colors

RATE = ['★'*i for i in range(1, 6)]  # 歌曲评分
PRO = on_light_red(' PRO ')
LOVE = ' ❤ '
PREFIX_SELECTED = '  > '
PREFIX_DESELECTED = '    '
SUFFIX_SELECTED = ''
SUFFXI_DESELECTED = ''


class MainDal(object):

    def __init__(self, data):
        self.c = db_config.theme
        self.lines = data.lines

        playingsong = data.playlist.get_playingsong()
        self.song_total_time = playingsong['length']
        self.song_kbps = playingsong['kbps'] + 'kbps'
        self.song_rate = RATE[int(round(playingsong['rating_avg'])) - 1]
        self.song_pro = '' if playingsong['kbps'] == '64' else PRO
        self.song_title = playingsong['title']
        self.song_albumtitle = playingsong['albumtitle']
        self.song_artist = playingsong['artist']
        self.song_public_time = playingsong['public_time']

        self.vol = data.vol
        self.loop = data.loop
        self.time = data.time

    def set_time(self, time):
        """
        时间状态
        """
        rest_time = int(self.song_total_time) - self.time - 1
        minute = int(rest_time) / 60
        sec = int(rest_time) % 60

        return str(minute).zfill(2) + ':' + str(sec).zfill(2)

    @property
    def title(self):

        time = self.set_time(self.time)

        title = [
            color_func(self.c['TITLE']['pro'])(self.song_pro),
            color_func(self.c['TITLE']['kbps'])(self.song_kbps),
            color_func(self.c['TITLE']['time'])(time),
            color_func(self.c['TITLE']['rate'])(self.song_rate),
            color_func(self.c['TITLE']['vol'])(self.vol),
            color_func(self.c['TITLE']['state'])(self.loop)]

        return ' '.join(title)

    @property
    def love(self):
        return color_func(self.c['PLAYINGSONG']['like'])(LOVE)

    @property
    def prefix_selected(self):
        return color_func(self.c['LINE']['arrow'])(PREFIX_SELECTED)

    @property
    def prefix_deselected(self):
        return PREFIX_DESELECTED

    @property
    def suffix_selected(self):
        love = self.love
        title = color_func(self.c['PLAYINGSONG']['title']) \
                          (self.song_title)
        albumtitle = color_func(self.c['PLAYINGSONG']['albumtitle']) \
                               (self.song_albumtitle)
        artist = color_func(self.c['PLAYINGSONG']['artist']) \
                           (self.song_artist)
        public_time = color_func(self.c['PLAYINGSONG']['publictime']) \
                                (self.song_public_time) or ''
        return (
            love +
            title + ' • ' +
            albumtitle + ' • ' +
            artist + ' ' +
            public_time
        ).replace('\\', '')

    @property
    def suffix_deselected(self):
        return SUFFXI_DESELECTED
