#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
数据层
"""
from API.api import Doubanfm
import Queue
from threading import RLock

douban = Doubanfm()

mutex = RLock()


class Playlist(object):

    def __init__(self):
        self._playlist = Queue.Queue(0)
        self._playingsong = None

    def lock(func):
        """
        互斥锁, 类中各个方法互斥
        """
        def _func(self):
            mutex.acquire()
            try:
                return func(self)
            finally:
                mutex.release()
        return _func

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

    @lock
    def get_song(self):
        """
        获取歌曲, 如果获取完歌曲列表为空则重新获取列表
        """
        if self._playlist.empty():
            self._get_list()

        song = self._playlist.get(1)  # 阻塞模式

        self._playingsong = song

        return song

    def get_playingsong(self):
        # if not self._playingsong:
        #     return self.get_song()
        return self._playingsong

    @lock
    def empty(self):
        """
        清空playlist
        """
        for _ in range(self._playlist.qsize()):
            self._playlist.get()

    @lock
    def is_empty(self):
        return self._playlist.empty


class History(object):

    def __init__(self):
        pass
