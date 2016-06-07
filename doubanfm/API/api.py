#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
豆瓣FM API
"""
import requests
import logging
import json

from doubanfm.config import db_config
from doubanfm.lrc2dic import lrc2dict
from doubanfm.API.json_utils import decode_dict
from doubanfm.exceptions import APIError


logger = logging.getLogger('doubanfm')  # get logger

HEADERS = {"User-Agent": "Paw/2.2.5 (Macintosh; OS X/10.11.1) GCDHTTPRequest"}


class Doubanfm(object):

    def __init__(self):
        """
        初始化:
            1. 获取本地data
            2. 获取频道列表
            3. 处理本地data, 装入post_data

        """
        self.login_data = db_config.login_data
        self._get_channels()
        self._cookies = self.login_data['cookies']
        self._channel_id = self._process_login_data()

    def _process_login_data(self):
        """
        return post_data
        """
        channel_id = self._get_channel_id(self.login_data['channel'])
        return channel_id

    def _get_channels(self):
        """
        获取channel列表
        """
        self._channel_list = [
            {'name': '红心兆赫', 'channel_id': -3},
            {'name': '我的私人兆赫', 'channel_id': 0},
            {'name': '每日私人歌单', 'channel_id': -2},
            {'name': '豆瓣精选兆赫', 'channel_id': -10},
            # 心情 / 场景
            {'name': '工作学习', 'channel_id': 153},
            {'name': '户外', 'channel_id': 151},
            {'name': '休息', 'channel_id': 152},
            {'name': '亢奋', 'channel_id': 154},
            {'name': '舒缓', 'channel_id': 155},
            {'name': 'Easy', 'channel_id': 77},
            {'name': '咖啡', 'channel_id': 32},
            # 语言 / 年代
            {'name': '华语', 'channel_id': 1},
            {'name': '欧美', 'channel_id': 2},
            {'name': '七零', 'channel_id': 3},
            {'name': '八零', 'channel_id': 4},
            {'name': '九零', 'channel_id': 5},
            {'name': '粤语', 'channel_id': 6},
            {'name': '日语', 'channel_id': 17},
            {'name': '韩语', 'channel_id': 18},
            {'name': '法语', 'channel_id': 22},
            {'name': '新歌', 'channel_id': 61},
            # 风格 / 流派
            {'name': '流行', 'channel_id': 194},
            {'name': '摇滚', 'channel_id': 7},
            {'name': '民谣', 'channel_id': 8},
            {'name': '轻音乐', 'channel_id': 9},
            {'name': '电影原声', 'channel_id': 10},
            {'name': '爵士', 'channel_id': 13},
            {'name': '电子', 'channel_id': 14},
            {'name': '说唱', 'channel_id': 15},
            {'name': 'R&B', 'channel_id': 16},
            {'name': '古典', 'channel_id': 27},
            {'name': '动漫', 'channel_id': 28},
            {'name': '世界音乐', 'channel_id': 187},
            {'name': '布鲁斯', 'channel_id': 188},
            {'name': '拉丁', 'channel_id': 189},
            {'name': '雷鬼', 'channel_id': 190},
            {'name': '小清新', 'channel_id': 76}
        ]

    def _get_channel_id(self, line):
        """
        把行数转化成channel_id
        """
        return self._channel_list[line]['channel_id']

    def _change_channel(self, fcid, tcid):
        """
        这个貌似没啥用
        :params fcid, tcid: string
        """
        url = 'https://douban.fm/j/change_channel'
        options = {
            'fcid': fcid,
            'tcid': tcid,
            'area': 'system_chis'
        }
        requests.get(url, params=options, cookies=self._cookies, headers=HEADERS)

    def set_channel(self, line):
        self._channel_id = self._channel_list[line]['channel_id']

    @property
    def channels(self):
        """
        格式化频道列表，以便display

        :params lines: list
        """
        lines = [ch['name'] for ch in self._channel_list]
        return lines

    def get_daily_songs(self):
        url = 'https://douban.fm/j/v2/songlist/user_daily/?kbps=320'
        s = requests.get(url, cookies=self._cookies, headers=HEADERS)
        req_json = s.json()
        # TODO: 验证
        return req_json['songs']

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
        options = {
            'type': ptype,
            'pt': '3.1',
            'channel': self._channel_id,
            'pb': '320',
            'from': 'mainsite',
            'r': '',
            'kbps': '320',
            'app_name': 'radio_website',
            'client': 's:mainsite|y:3.0',
            'version': '100'
        }
        if 'sid' in data:
            options['sid'] = data['sid']
        url = 'https://douban.fm/j/v2/playlist'
        while 1:
            try:
                s = requests.get(url, params=options, cookies=self._cookies, headers=HEADERS)
                req_json = s.json()
                if req_json['r'] == 0:
                    if 'song' not in req_json:
                        break
                    return req_json['song'][0]
            except Exception, err:
                raise APIError(err)
                break

    def get_first_song(self):
        """
        初始获取歌曲

        :params return: json
        """
        return self.requests_url('n')

    def get_song(self, sid):
        """
        获取歌曲

        :params sid: 歌曲sid string
        """
        return self.requests_url('p', sid=sid)

    def skip_song(self, sid):
        """
        跳过歌曲

        return: list
        """
        return self.requests_url('s', sid=sid)

    def bye(self, sid):
        """
        不再播放

        : params sid: string
        : return: list
        """
        return self.requests_url('b', sid=sid)

    def rate_music(self, sid):
        """
        标记喜欢歌曲, 返回新的下一首歌
        """
        return self.requests_url('r', sid=sid)

    def unrate_music(self, sid):
        """
        取消标记喜欢歌曲
        """
        return self.requests_url('u', sid=sid)

    def submit_music(self, sid):
        """
        歌曲结束标记
        """
        self.requests_url('e', sid=sid)

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
            url = "https://api.douban.com/v2/fm/lyric"
            postdata = {
                'sid': playingsong['sid'],
                'ssid': playingsong['ssid'],
            }
            s = requests.session()
            response = s.post(url, data=postdata, headers=HEADERS)

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
