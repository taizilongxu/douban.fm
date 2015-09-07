#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
豆瓣FM API
"""
import requests
import getpass
import urllib
import logging
import json
from douban.config import db_config
from douban.lrc2dic import lrc2dict

LOGO = '''
[38;5;202m⡇       ⡆  ⡀    ⣄       ⣆       ⡄⢀      ⢀⡄          ⡄              ⢠⡇           (B[m
[38;5;214m⡇      ⢰⡇  ⣿    ⡗⢤      ⡏⡆    ⢸⣼⠘⢾      ⢸⡇ ⡄       ⢰⡇ ⣴   ⣰     ⡀  ⡇⡇       ⢀⢧  (B[m
[38;5;226m⡇      ⢸⢇  ⣿   ⢀⠇⠘⡄     ⡇⡇    ⡇⠁ ⠘⡄  ⢸⡀ ⡎⡇⢰⢹       ⡜⡇⢰⠁⢇ ⢠⢿  ⢸⢆ ⣇  ⡇⡇  ⣄    ⢸⢸  (B[m
[38;5;190m⡇     ⢀⠇⢸  ⡏⡆  ⢸  ⡇⣷   ⢸ ⡇    ⡇   ⡇  ⢸⡇ ⡇⢱⡎⢸    ⡆  ⡇⢸⢸ ⢸ ⢸⠘⡄ ⢸⢸⢀⢿  ⡇⢱⢀ ⣿ ⢸⡀ ⢸⠈⡆ (B[m
[38;5;154m⡇     ⢸ ⢸⢰ ⡇⡇  ⢸  ⣇⠟⡄  ⢸ ⢣   ⣠⠃   ⡇  ⡸⡇⢰⠁⢸⠇⢸ ⡀ ⢰⢹  ⡇⢸⢸ ⠸⡀⢸ ⡇ ⡸⢸⢸⠸⡀⢠⠃⢸⢸⡄⡿⡀⡇⡇ ⢸ ⡇ (B[m
[38;5;82m⡇  ⣦  ⡇ ⢸⢸⣿ ⢱  ⢸  ⢸ ⢣  ⢸ ⢸  ⡜⠈    ⡇⣄ ⡇⢱⢸ ⠘ ⠸⣸⢣ ⢸⠘⢤⢀⠇⢸⡇  ⡇⡸ ⡇ ⡇ ⣿ ⡇⢸ ⢸⢸⣿ ⠗⠁⢱ ⢸ ⡇ (B[m
[38;5;46m⡇  ⣿  ⡇ ⢸⡇⣿ ⢸  ⡸    ⠘⢄ ⢸ ⢸ ⢠⠃     ⡇⣿ ⡇⠘⡼    ⡿⠸⡀⡇  ⣿ ⢸⡅  ⡇⡇ ⢣ ⡇ ⣿ ⢣⢸ ⢸⡜⠸   ⠸⡀⢸ ⡇ (B[m
[38;5;48m⣧⠒⣴⢹ ⣀⠇ ⠸⡇⢻  ⠱⡀⡅      ⡇⢸  ⡇⢸      ⡇⣿ ⡇ ⠁    ⠇ ⡇⡇  ⢿ ⢸⡇  ⢸⡇ ⠘⡄⡇ ⡟ ⢸⠎ ⢸⡇     ⡇⡇ ⡇⡇(B[m
[38;5;50m⡟ ⠻ ⡿⠹   ⠁⠘   ⣇⠇      ⠈⠇  ⢇⠇      ⢳⠉⣦⠃        ⣷⠁  ⠈  ⠇  ⢸⡇  ⠉⠃      ⢸⡇     ⢸⡇ ⢱⠇(B[m
[38;5;51m⠁   ⠁         ⢻           ⠈       ⢸ ⠏         ⢹         ⠘⠇          ⠈⡇      ⠇ ⠸ (B[m
'''

logger = logging.getLogger(__name__)  # get logger


def _decode_list(data):
    """解析json列表,转换成utf-8"""
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        rv.append(item)
    return rv


def _decode_dict(data):
    """解析json字典,转换成utf-8"""
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')

        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        # no need to recurse into dict, json library will do that
        rv[key] = value
    return rv


def win_login():
    """登陆界面"""
    email = raw_input('Email: ')
    password = getpass.getpass('Password: ')
    return email, password



class Doubanfm(object):

    def __init__(self):
        """初始化获取频道列表
        :param login_data:{'user_id': user_id,
                           'expire': exprie,
                           'token': token,
                           'channel': channel}
        """
        self.login_data = db_config.login_data
        self.get_channels()
        self.post_data = self.process_login_data()

    def process_login_data(self):
        """post_data"""
        channel_id = self.get_channel_id(self.login_data['channel'])
        post_data = {'app_name': 'radio_desktop_win',  # 固定
                     'version': 100,  # 固定
                     'user_id': self.login_data['user_id'],  # 登录必填
                     'expire': self.login_data['expire'],  # 登录必填
                     'token': self.login_data['token'],  # 登录必填
                     'channel': channel_id}  # 可选项
        return post_data

    def get_channels(self):
        """获取channel列表，将channel name/id存入self._channel_list"""
        # 红心兆赫需要手动添加
        self._channel_list = [{
            'name': '红心兆赫',
            'channel_id': -3
        }]
        r = requests.get('http://www.douban.com/j/app/radio/channels')
        self._channel_list += json.loads(r.text, object_hook=_decode_dict)['channels']

    def get_channel_id(self, line):
        """把行数转化成channel_id"""
        return self._channel_list[line]['channel_id']

    def set_channel(self, line):
        self.post_data['channel'] = self._channel_list[line]['channel_id']

    @property
    def channels(self):
        """返回channel名称列表（一个list，不包括id）"""
        # 格式化频道列表，以便display
        lines = [ch['name'] for ch in self._channel_list]
        return lines

    def requests_url(self, ptype, **data):
        """这里包装了一个函数,发送post_data
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
        """获取播放列表,返回一个list"""
        s = self.requests_url('n')
        return json.loads(s, object_hook=_decode_dict)['song']

    def skip_song(self, playingsong):
        """下一首,返回一个list
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
        """
        s = self.requests_url('s', sid=playingsong['sid'])
        return json.loads(s, object_hook=_decode_dict)['song']

    def bye(self, playingsong):
        """不再播放,返回一个list"""
        s = self.requests_url('b', sid=playingsong['sid'])
        return json.loads(s, object_hook=_decode_dict)['song']

    def rate_music(self, playingsong):
        """标记喜欢歌曲"""
        self.requests_url('r', sid=playingsong['sid'])

    def unrate_music(self, playingsong):
        """取消标记喜欢歌曲"""
        self.requests_url('u', sid=playingsong['sid'])

    def submit_music(self, playingsong):
        """歌曲结束标记"""
        self.requests_url('e', sid=playingsong['sid'])

    def get_lrc(self, playingsong):
        """获取歌词"""
        try:
            url = "http://api.douban.com/v2/fm/lyric"
            postdata = {
                'sid': playingsong['sid'],
                'ssid': playingsong['ssid'],
            }
            s = requests.session()
            response = s.post(url, data=postdata)
            lyric = json.loads(response.text, object_hook=_decode_dict)
            logger.debug(response.text)
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


def main():
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    douban = Doubanfm()
    douban.init_login()  # 登录
    print douban.login_data
    print douban.channels
    print douban.get_playlist()

if __name__ == '__main__':
    main()
