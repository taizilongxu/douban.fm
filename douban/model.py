#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
数据层
"""
from API.api import Doubanfm
import Queue
from threading import Lock

douban = Doubanfm()

mutex = Lock()


class Playlist(object):

    def __init__(self):
        self._playlist = Queue.Queue(0)

    def lock(args):
        """
        互斥锁, 类中各个方法互斥
        """
        def _deco(func):
            def _func(self):
                mutex.acquire()
                func(self)
                mutex.release()
            return _func
        return _deco

    @lock
    def get_list(self, channel=None):
        """
        获取歌词列表, 如果channel不为空则重新设置频道

        :params channel: int
        """
        if channel:
            douban.set_channel(channel)

        for i in douban.get_playlist():
            self._playlist.put(i)

    @lock
    def get_song(self):
        """
        获取歌曲, 如果获取完歌曲列表为空则重新获取列表
        """
        song = self._playlist.get(1)  # 阻塞模式

        if self._playlist.empty():
            self.get_list()
        return song

    @lock
    def empty(self):
        """
        清空playlist
        """
        for _ in range(self._playlist.qsize()):
            self._playlist.get()



class History(object):

    def __init__(self):
        pass
