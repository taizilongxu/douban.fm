#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
处理main_view的数据

control和view中间层, 负责生成显示的内容(增加主题色彩)

    dal = MainDal(data)

    dal.title
    dal.love
    dal.prefix_selected
    dal.prefix_deselected
    dal.suffix_selected
    dal.suffix_deselected
    dal.lines
"""
import logging

from doubanfm.colorset.colors import on_light_red, color_func  # colors

logger = logging.getLogger('doubanfm')

RATE = ['★'*i for i in range(1, 6)]  # 歌曲评分
PRO = on_light_red(' PRO ')
LOVE = ' ❤  '
PREFIX_SELECTED = '  > '
PREFIX_DESELECTED = '    '
SUFFIX_SELECTED = ''
SUFFXI_DESELECTED = ''


class MainDal(object):

    def __init__(self, data):
        self.c = data.theme
        self.data = data

        playingsong = data.playlist.get_playingsong()
        self.song_total_time = playingsong['length']
        self.song_kbps = playingsong['kbps'] + 'kbps'
        # self.song_rate = RATE[int(round(playingsong.get('rating_avg', 0))) - 1]
        self.song_pro = '' if playingsong['kbps'] == '128' else PRO
        self.song_title = playingsong['title']
        self.song_albumtitle = playingsong['albumtitle']
        self.song_artist = playingsong['artist']
        # self.song_public_time = playingsong['public_time']

        self.song_like = data.song_like
        self.netease = data.netease
        self.volume = data.volume
        self.loop = data.loop
        self.pause = data.pause
        self.time = data.time
        self.user_name = data.user_name

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
        volume = str(self.volume) + '%' if self.volume != 0 else \
                 color_func(self.c['TITLE']['state'])('✖')

        if self.pause:
            loop = 'P'
        elif self.loop:
            loop = '⟲'
        else:
            loop = '→'

        source = '网易' if self.netease else ''

        title = [
            PREFIX_DESELECTED,
            color_func(self.c['TITLE']['doubanfm'])('DoubanFM'),
            '\\',
            color_func(self.c['TITLE']['username'])(self.user_name),
            '>>',
            # color_func(self.c['TITLE']['pro'])(self.song_pro),
            color_func(self.c['PLAYINGSONG']['like'])(source),
            color_func(self.c['TITLE']['kbps'])(self.song_kbps),
            color_func(self.c['TITLE']['time'])(time),
            # color_func(self.c['TITLE']['rate'])(self.song_rate),
            color_func(self.c['TITLE']['vol'])(volume),
            color_func(self.c['TITLE']['state'])(loop)]

        return ' '.join(title)

    @property
    def love(self):
        if self.song_like == 1:
            return color_func(self.c['PLAYINGSONG']['like'])(LOVE)
        else:
            return ''

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
        # public_time = color_func(self.c['PLAYINGSONG']['publictime']) \
        #                         (self.song_public_time) or ''
        return (
            love +
            title + ' • ' +
            albumtitle + ' • ' +
            artist + ' '
            # public_time
        ).replace('\\', '')

    @property
    def suffix_deselected(self):
        return SUFFXI_DESELECTED

    @property
    def lines(self):
        return self.data.lines
