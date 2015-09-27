#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
数据层
"""
from threading import RLock
import functools
import Queue

from doubanfm.API.api import Doubanfm
from doubanfm.API.netease_api import Netease
from doubanfm.config import db_config

douban = Doubanfm()

mutex = RLock()


class Playlist(object):
    """
    播放列表, 各个方法互斥

    使用方法:

        playlist = Playlist()

        playingsong = playlist.get_song()

        获取当前播放歌曲
        playingsong = playlist.get_playingsong()
    """

    def __init__(self):
        self._playlist = Queue.Queue(0)
        self._playingsong = None

        # 根据歌曲来改变歌词
        self._lrc = {}
        self._pre_playingsong = None

    def lock(func):
        """
        互斥锁
        """
        @functools.wraps(func)
        def _func(*args, **kwargs):
            mutex.acquire()
            try:
                return func(*args, **kwargs)
            finally:
                mutex.release()
        return _func

    def get_lrc(self):
        """
        返回当前播放歌曲歌词
        """
        if self._playingsong != self._pre_playingsong:
            self._lrc = douban.get_lrc(self._playingsong)
            self._pre_playingsong = self._playingsong
        return self._lrc

    def set_channel(self, channel_num):
        """
        设置api发送的FM频道

        :params channel_num: channel_list的索引值 int
        """
        douban.set_channel(channel_num)

    @lock
    def _get_list(self, channel=None):
        """
        获取歌词列表, 如果channel不为空则重新设置频道

        :params channel: int
        """
        if channel:
            douban.set_channel(channel)
            self.empty()

        for i in douban.get_playlist():
            self._playlist.put(i)

    def set_song_like(self):
        douban.rate_music(self._playingsong)

    def set_song_unlike(self):
        douban.unrate_music(self._playingsong)

    @lock
    def bye(self):
        """
        不再播放, 返回新列表
        """
        for i in douban.bye(self._playingsong):
            self._playlist.put(i)

    @lock
    def get_song(self, netease=False):
        """
        获取歌曲, 如果获取完歌曲列表为空则重新获取列表
        """
        if self._playlist.empty():
            self._get_list()

        song = self._playlist.get(True)

        # 网易320k音乐
        if netease:
            url, kbps = Netease().get_url_and_bitrate(song['title'])
            if url and kbps:
                song['url'], song['kbps'] = url, kbps

        self._playingsong = song

        return song

    @lock
    def get_playingsong(self):
        return self._playingsong

    @lock
    def empty(self):
        """
        清空playlist
        """
        self._playlist.clear()


class History(object):

    def __init__(self):
        db_config.history


class Channel(object):

    def __init__(self):
        self.lines = douban.channels
