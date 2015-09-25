#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
豆瓣FM API
"""
import requests
import logging
import urllib
import json
import sys

from doubanfm.config import db_config
from doubanfm.lrc2dic import lrc2dict
from doubanfm.API.json_utils import decode_dict


logger = logging.getLogger('doubanfm')  # get logger


class Doubanfm(object):

    def __init__(self):
        """
        初始化:
            1. 获取本地data
            2. 获取频道列表
            3. 处理本地data, 装入post_data

        :param post_data:{'app_name': 'radio_desktop_win',
                          'version': 100,
                          'user_id': user_id,
                          'expire': exprie,
                          'token': token,
                          'channel': channel}
        """
        self.login_data = db_config.login_data
        self._get_channels()
        self.post_data = self._process_login_data()

    def _process_login_data(self):
        """
        return post_data
        """
        channel_id = self._get_channel_id(self.login_data['channel'])
        post_data = {'app_name': 'radio_desktop_win',  # 固定
                     'version': 100,  # 固定
                     'user_id': self.login_data['user_id'],  # 登录必填
                     'expire': self.login_data['expire'],  # 登录必填
                     'token': self.login_data['token'],  # 登录必填
                     'channel': channel_id}  # 可选项
        return post_data

    def _get_channels(self):
        """
        获取channel列表，将channel name/id存入self._channel_list
        """
        # 红心兆赫需要手动添加
        self._channel_list = [{
            'name': '红心兆赫',
            'channel_id': -3
        }]
        try:
            r = requests.get('http://www.douban.com/j/app/radio/channels')
        except requests.exceptions.ConnectionError:
            print 'ConnectionError'
            sys.exit()
        try:
            self._channel_list += json.loads(r.text, object_hook=decode_dict)['channels']
        except ValueError:
            print '403 Forbidden'
            sys.exit()

    def _get_channel_id(self, line):
        """
        把行数转化成channel_id
        """
        return self._channel_list[line]['channel_id']

    def set_channel(self, line):
        self.post_data['channel'] = self._channel_list[line]['channel_id']

    @property
    def channels(self):
        """
        格式化频道列表，以便display

        :params lines: list
        """
        lines = [ch['name'] for ch in self._channel_list]
        return lines

    def requests_url(self, ptype, **data):
        """
        这里包装了一个函数,发送post_data
        :param ptype: n 列表无歌曲,返回新列表
                      e 发送歌曲完毕
                      b 不再播放,返回新列表
                      s 下一首,返回新的列表
                      r 标记喜欢
                      u 取消标记喜欢
        """
        post_data = self.post_data.copy()
        post_data['type'] = ptype
        for x in data:
            post_data[x] = data[x]
        url = 'http://www.douban.com/j/app/radio/people?' + urllib.urlencode(post_data)
        try:
            s = requests.get(url)
        except requests.exceptions.RequestException:
            logger.error("Error communicating with Douban.fm API.")
        return s.text

    def get_playlist(self):
        """
        获取播放列表

        :params return: list
        """
        s = self.requests_url('n')
        return json.loads(s, object_hook=decode_dict)['song']

    def skip_song(self, playingsong):
        """
        跳过歌曲

        :param playingsong: {
                "album": "/subject/5952615/",
                "picture": "http://img3.douban.com/mpic/s4616653.jpg",
                "ssid": "e1b2",
                "artist": "Bruno Mars / B.o.B",
                "url": "http://mr3.douban.com/201308250247/4a3de2e8016b5d659821ec76e6a2f35d/view/song/small/p1562725.mp3",
                "company": "EMI",
                "title": "Nothin' On You",
                "rating_avg": 4.04017,
                "length": 267,
                "subtype": "",
                "public_time": "2011",
                "sid": "1562725",
                "aid": "5952615",
                "sha256": "2422b6fa22611a7858060fd9c238e679626b3173bb0d161258b4175d69f17473",
                "kbps": "64",
                "albumtitle": "2011 Grammy Nominees",
                "like": 1
            }
        return: list
        """
        s = self.requests_url('s', sid=playingsong['sid'])
        return json.loads(s, object_hook=decode_dict)['song']

    def bye(self, playingsong):
        """
        不再播放
        
        : params playingsong
        : return: list
        """
        s = self.requests_url('b', sid=playingsong['sid'])
        return json.loads(s, object_hook=decode_dict)['song']

    def rate_music(self, playingsong):
        """
        标记喜欢歌曲
        """
        self.requests_url('r', sid=playingsong['sid'])

    def unrate_music(self, playingsong):
        """
        取消标记喜欢歌曲
        """
        self.requests_url('u', sid=playingsong['sid'])

    def submit_music(self, playingsong):
        """
        歌曲结束标记
        """
        self.requests_url('e', sid=playingsong['sid'])

    def get_lrc(self, playingsong):
        """
        获取歌词

        如果测试频繁会发如下信息:
        {'msg': 'You API access rate limit has been exceeded.
                 Contact api-master@douban.com if you want higher limit. ',
         'code': 1998,
         'request': 'POST /v2/fm/lyric'}
        """
        try:
            url = "http://api.douban.com/v2/fm/lyric"
            postdata = {
                'sid': playingsong['sid'],
                'ssid': playingsong['ssid'],
            }
            s = requests.session()
            response = s.post(url, data=postdata)

            # 把歌词解析成字典
            lyric = json.loads(response.text, object_hook=decode_dict)
            if lyric.get('code', None) == 1998:
                logger.info('lrc API access rate limit has been exceeded')
                return {}
            lrc_dic = lrc2dict(lyric['lyric'])

            # 原歌词用的unicode,为了兼容
            for key, value in lrc_dic.iteritems():
                lrc_dic[key] = value.decode('utf-8')
            if lrc_dic:
                logger.debug('Get lyric success!')
            return lrc_dic
        except requests.exceptions.RequestException:
            logger.error('Get lyric failed!')
            return {}
