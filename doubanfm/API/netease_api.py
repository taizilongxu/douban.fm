#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
网易云音乐API

根据歌名提供320k音乐url地址
reference: https://github.com/yanunon/NeteaseCloudMusic/wiki/%E7%BD%91%E6%98%93%E4%BA%91%E9%9F%B3%E4%B9%90API%E5%88%86%E6%9E%90
TODO: 有可能歌曲匹配不准确
"""
import requests
import json
import md5
import logging

logger = logging.getLogger('doubanfm')  # get logger


class Netease(object):

    def __init__(self):
        pass

    def search(self, song_title, limit=1):
        """
        根据歌曲名搜索歌曲

        : params : song_title: 歌曲名
                   limit: 搜索数量
        """
        url = "http://music.163.com/api/search/pc"
        headers = {'Cookie': 'appver=1.5.2',
                   'Referer': 'http://music.163.com'}
        payload = {'s': song_title,
                   'limit': limit,
                   'type': 1}

        r = requests.post(url, params=payload, headers=headers)
        data = json.loads(r.text)

        if data['code'] == 200:
            return data['result']['songs'][0]
        else:
            return None

    def get_song_id(self, song_title):
        """
        根据歌名获取歌曲id
        """
        song = self.search(song_title)

        if song.get('hMusic', None):
            return song['hMusic']['dfsId'], song['hMusic']['bitrate']
        elif song.get('mMusic', None):
            return song['mMusic']['dfsId'], song['mMusic']['bitrate']
        elif song.get('lMusic', None):
            return song['lMusic']['dfsId'], song['lMusic']['bitrate']
        return None

    def get_url_and_bitrate(self, song_title):
        """
        根据歌名搜索320k地址
        """
        song_id, bitrate = self.get_song_id(song_title)
        url = 'http://m1.music.126.net/'
        if song_id:
            url += self.encrypted_id(song_id) + '/' + str(song_id) + '.mp3'
            bitrate = str(bitrate/1000)
            return url, bitrate
        else:
            return None, None

    def encrypted_id(self, id):
        id = str(id)
        byte1 = bytearray('3go8&$8*3*3h0k(2)2')
        byte2 = bytearray(id)
        byte1_len = len(byte1)
        for i in xrange(len(byte2)):
            byte2[i] = byte2[i]^byte1[i%byte1_len]
        m = md5.new()
        m.update(byte2)
        result = m.digest().encode('base64')[:-1]
        result = result.replace('/', '_')
        result = result.replace('+', '-')
        return result

if __name__ == '__main__':
    url, bitrate = Netease().get_url_and_bitrate("董小姐")
    print url
    print bitrate
