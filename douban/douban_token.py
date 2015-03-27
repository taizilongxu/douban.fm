#!/usr/bin/env python
# encoding: utf-8
"""
豆瓣FM的网络连接部分
主要完成登录部分
例如:
douban = douban_token.Doubanfm()
douban.init_login()  #登录

playingsong =
{
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
from functools import wraps
from scrobbler import Scrobbler
import requests
import lrc2dic
import getpass
import pickle
import urllib
import logging
import sys
import os

logger = logging.getLogger()


class Doubanfm(object):
    def __init__(self):
        self.login_data = {}
        self.lastfm = True  # lastfm 登陆

    def init_login(self):
        print '''
        ──╔╗─────╔╗────────╔═╗
        ──║║─────║║────────║╔╝
        ╔═╝╠══╦╗╔╣╚═╦══╦═╗╔╝╚╦╗╔╗
        ║╔╗║╔╗║║║║╔╗║╔╗║╔╗╬╗╔╣╚╝║
        ║╚╝║╚╝║╚╝║╚╝║╔╗║║║╠╣║║║║║
        ╚══╩══╩══╩══╩╝╚╩╝╚╩╩╝╚╩╩╝

        '''
        self.douban_login()  # 登陆
        self.login_lastfm()  # 登陆 last.fm
        print '\033[31m♥\033[0m Get channels ',
        # self.get_channels()  # 获取频道列表
        print '[\033[32m ok \033[0m]'
        # self.get_channellines()  # 重构列表用以显示
        print '\033[31m♥\033[0m Check pro ',
        # self.is_pro()
        print '[\033[32m ok \033[0m]'
        # if self.pro == 1:
        #     self.login_data['kbps'] = 192  # 128 64 歌曲kbps的选择

    # def is_pro(self):
    #     '''查看是否是pro用户'''
    #     self.get_playlist()
    #     self.get_song()
    #     if int(self.playingsong['kbps']) != 64:
    #         self.pro = 1

    def win_login(self):
        '''登陆界面'''
        email = raw_input('email:')
        password = getpass.getpass('password:')
        return email, password

    def login_lastfm(self):
        '''last.fm登陆'''
        if self.lastfm and self.last_fm_username and self.last_fm_password:
            self.scrobbler = Scrobbler(
                self.last_fm_username, self.last_fm_password)
            r, err = self.scrobbler.handshake()
            if r:
                logger.info("Last.fm logged success!")
                print '\033[31m♥\033[0m Loging Last.fm : %s' % self.last_fm_username
            else:
                logger.error("Last.fm 登录失败: " + err)
                self.lastfm = False
        else:
            self.lastfm = False

    def last_fm_account_required(fun):
        '''装饰器，用于需要登录last.fm后才能使用的接口'''
        @wraps(fun)
        def wrapper(self, *args, **kwds):
            if not self.lastfm:
                return
            return fun(self, *args, **kwds)
        return wrapper

    @last_fm_account_required
    def submit_current_song(self):
        '''提交播放过的曲目'''
        # Submit the track if total playback time of the track > 30s
        if self.playingsong['length'] > 30:
            self.scrobbler.submit(
                self.playingsong['artist'],
                self.playingsong['title'],
                self.playingsong['albumtitle'],
                self.playingsong['length']
            )

    @last_fm_account_required
    def scrobble_now_playing(self):
        '''提交当前正在播放曲目'''
        self.scrobbler.now_playing(
            self.playingsong['artist'],
            self.playingsong['title'],
            self.playingsong['albumtitle'],
            self.playingsong['length']
        )

    def douban_login(self):
        '''登陆douban.fm获取token'''
        path_token = os.path.expanduser('~/.douban_token.txt')
        if os.path.exists(path_token):
            # 已登陆
            with open(path_token, 'r') as f:
                self.login_data = pickle.load(f)
                self.token = self.login_data['token']
                self.user_name = self.login_data['user_name']
                self.user_id = self.login_data['user_id']
                self.expire = self.login_data['expire']
                self.default_volume = int(self.login_data['volume'])\
                        if 'volume' in self.login_data else 50
                self.default_channel = int(self.login_data['channel'])\
                        if 'channel' in self.login_data else 1

                # 存储的default_channel是行数而不是真正发送数据的channel_id
                # 这里需要进行转化一下
                self.set_channel(self.default_channel)
            print '\033[31m♥\033[0m Get local token - user_name: \033[33m%s\033[0m' % self.user_name
        else:
            # 未登陆
            logger.info('First time logging in douban.fm')
            while True:
                self.email, self.password = self.win_login()
                login_data = {
                        'app_name': 'radio_desktop_win',
                        'version': '100',
                        'email': self.email,
                        'password': self.password
                        }
                s = requests.post('http://www.douban.com/j/app/login', login_data)
                dic = eval(s.text)
                if dic['r'] == 1:
                    logger.debug(dic['err'])
                    continue
                else:
                    self.token = dic['token']
                    self.user_name = dic['user_name']
                    self.user_id = dic['user_id']
                    self.expire = dic['expire']
                    self.default_volume = 50
                    self.default_channel = 1
                    self.login_data = {
                        'app_name': 'radio_desktop_win',
                        'version': '100',
                        'user_id': self.user_id,
                        'expire': self.expire,
                        'token': self.token,
                        'user_name': self.user_name,
                        'volume': '50',
                        'channel': '0'
                    }
                    logger.info('Logged in username: ' + self.user_name)
                    with open(path_token, 'w') as f:
                        pickle.dump(self.login_data, f)
                        logger.debug('Write data to ' + path_token)
                    break

        self.last_fm_username = \
            self.login_data['last_fm_username'] if 'last_fm_username' in self.login_data\
            else None
        self.last_fm_password = \
            self.login_data['last_fm_password'] if 'last_fm_password' in self.login_data\
            else None
        # last.fm登陆
        try:
            if sys.argv[1] == 'last.fm':
                from hashlib import md5
                username = raw_input('last.fm username:') or None
                password = getpass.getpass('last.fm password:') or None
                if username and password:
                    self.last_fm_username = username
                    self.last_fm_password = md5(password).hexdigest()
                with open(path_token, 'r') as f:
                    data = pickle.load(f)
                with open(path_token, 'w') as f:
                    data['last_fm_username'] = username
                    data['last_fm_password'] = self.last_fm_password
                    pickle.dump(data, f)
        except IndexError:
            pass

        # 配置文件
        path_config = os.path.expanduser('~/.doubanfm_config')
        if not os.path.exists(path_config):
            print '\033[31m♥\033[0m Get default config [\033[32m ok \033[0m]'
            config = '''[key]
UP = k
DOWN = j
TOP = g
BOTTOM = G
OPENURL = w
RATE = r
NEXT = n
BYE = b
QUIT = q
PAUSE = p
LOOP = l
MUTE = m
LRC = o
'''  # 这个很丑,怎么办
            with open(path_config, 'w') as F:
                F.write(config)
        else:
            print '\033[31m♥\033[0m Get local config [\033[32m ok \033[0m]'

    @property
    def channels(self):
        '''获取channel，存入self.channels'''
        # 红心兆赫需要手动添加
        channels = [{
            'name': '红心兆赫',
            'channel_id': -3
        }]
        r = requests.get('http://www.douban.com/j/app/radio/channels')
        channels += eval(r.text)['channels']
        # 格式化频道列表，以便display
        lines = []
        for channel in channels:
            lines.append(channel['name'])
        return lines

    def requests_url(self, ptype, **data):
        '''这里包装了一个函数,发送post_data'''
        post_data = self.login_data.copy()
        post_data['type'] = ptype
        for x in data:
            post_data[x] = data[x]
        url = 'http://www.douban.com/j/app/radio/people?' + urllib.urlencode(post_data)
        s = requests.get(url)
        return s.text

    def set_channel(self, channel):
        '''把行数转化成channel_id'''
        self.default_channel = channel
        channel = -3 if channel == 0 else channel - 1
        self.login_data['channel'] = channel

    def get_playlist(self, channel):
        '''获取播放列表,返回一个list'''
        if self.default_channel != channel:
            self.set_channel(channel)
        s = self.requests_url('n')
        return eval(s)['song']

    def skip_song(self, playingsong):
        '''下一首,返回一个list'''
        s = self.requests_url('s', sid=playingsong['sid'])
        return eval(s)['song']

    def bye(self, playingsong):
        '''不再播放,返回一个list'''
        s = self.requests_url('b', sid=playingsong['sid'])
        return eval(s)['song']

    def rate_music(self, playingsong):
        '''标记喜欢歌曲'''
        s = self.requests_url('r', sid=playingsong['sid'])
        # self.playlist = eval(s)['song']

    def unrate_music(self, playingsong):
        '''取消标记喜欢歌曲'''
        s = self.requests_url('u', sid=playingsong['sid'])
        # self.playlist = eval(s)['song']

    def submit_music(self, playingsong):
        '''歌曲结束标记'''
        self.requests_url('e', sid=playingsong['sid'])

    def get_pic(self, playingsong, tempfile_path):
        '''获取专辑封面'''
        url = playingsong['picture'].replace('\\', '')
        for i in range(3):
            try:
                urllib.urlretrieve(url, tempfile_path)
                logger.debug('Get cover art success!')
                return True
            except (IOError, urllib.ContentTooShortError):
                pass
        logger.error('Get cover art failed!')
        return False

    def get_lrc(self, playingsong):
        '''获取歌词'''
        try:
            url = "http://api.douban.com/v2/fm/lyric"
            postdata = {
                'sid': playingsong['sid'],
                'ssid': playingsong['ssid'],
            }
            s = requests.session()
            response = s.post(url, data=postdata)
            lyric = eval(response.text)
            logger.debug(response.text)
            lrc_dic = lrc2dic.lrc2dict(lyric['lyric'])
            # 原歌词用的unicode,为了兼容
            for key, value in lrc_dic.iteritems():
                lrc_dic[key] = value.decode('utf-8')
            if lrc_dic:
                logger.debug('Get lyric success!')
            return lrc_dic
        except requests.exceptions.RequestException:
            logger.error('Get lyric failed!')
            return 0

def main():
    douban = Doubanfm()
    douban.init_login()  #登录
    print douban.login_data
    print douban.channels
    print douban.get_playlist(-3)

if __name__ == '__main__':
    main()
