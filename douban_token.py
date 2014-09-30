#-*- encoding: UTF-8 -*-
#---------------------------------import------------------------------------
import requests
import urllib
import json
import os
import pickle
#---------------------------------------------------------------------------
class Doubanfm(object):
    def __init__(self):
        self.login_data = {}
        self.channel_id = 0
        self.lines = [] # 要输出到终端的行
        # 红心兆赫需要手动添加
        self.channels = [{
            'name':'红心兆赫',
            'channel_id' : -3
            }]
        self.pro = 0
        self.playlist = []
        self.playingsong = {}
        self.login() # 登陆
        self.get_channels() # 获取频道列表
        self.get_channellines() # 重构列表用以显示
        self.is_pro()

    def is_pro(self):
        # 查看是否是pro用户
        self.get_playlist()
        self.get_song()
        if not int(self.playingsong['kbps']) == 64:
            self.pro = 1
        # 清空列表
        self.playingsong = {}

    def win_login(self):
        '登陆界面'
        email = raw_input('email:')
        password = raw_input('password:')
        return email,password

    def login(self):
        '登陆douban.fm获取token'
        if  os.path.exists('.douban_token.txt'):
            with open('.douban_token.txt', 'r') as f:
                self.login_data = pickle.load(f)
                self.token = self.login_data['token']
                self.user_name = self.login_data['user_name']
                self.user_id = self.login_data['user_id']
                self.expire = self.login_data['expire']
        else:
            self.email,self.password = self.win_login()
            login_data = {
                    'app_name': 'radio_desktop_win',
                    'version': '100',
                    'email': self.email,
                    'password': self.password
                    }
            s = requests.post('http://www.douban.com/j/app/login', login_data)
            dic = eval(s.text)
            if dic['r'] == '1':
                print dic['err']
            else:
                self.token = dic['token']
                self.user_name = dic['user_name']
                self.user_id = dic['user_id']
                self.expire = dic['expire']
                self.login_data = {
                    'app_name' : 'radio_desktop_win',
                    'version' : '100',
                    'user_id' : self.user_id,
                    'expire' : self.expire,
                    'token' : self.token,
                    'user_name' : self.user_name
                        }
                with open('.douban_token.txt','w') as f:
                    pickle.dump(self.login_data, f)

    def get_channels(self):
        '获取channel,c存入self.channels'
        r = requests.get('http://www.douban.com/j/app/radio/channels')
        self.channels += eval(r.text)['channels']

    def get_channellines(self):
        for index,channel in enumerate(self.channels):
            self.lines.append(channel['name'])

    # def select_channel(self,num):
    #     self.channel_num = num

    def get_playlist(self):
        '当playlist为空,获取播放列表'
        self.login_data['channel'] = self.channel_id
        post_data = self.login_data.copy()
        post_data['type'] = 'n'

        url = 'http://www.douban.com/j/app/radio/people?' + urllib.urlencode(post_data).strip()
        s = requests.get(url)
        self.playlist = eval(s.text)['song']

    def skip_song(self):
        '下一首'
        post_data = self.login_data.copy()
        post_data['type'] = 's'
        post_data['sid'] = self.playingsong['sid']

        url = 'http://www.douban.com/j/app/radio/people?' + urllib.urlencode(post_data).strip()
        s = requests.get(url)
        self.playlist = eval(s.text)['song']

    def bye(self):
        'bye,不再播放'
        post_data = self.login_data.copy()
        post_data['type'] = 'b'
        post_data['sid'] = self.playingsong['sid']

        url = 'http://www.douban.com/j/app/radio/people?' + urllib.urlencode(post_data).strip()
        s = requests.get(url)
        self.playlist = eval(s.text)['song']

    def set_channel(self, num):
        self.channel_id = num

    def get_song(self):
        if not self.playlist:
            self.get_playlist()
        self.playingsong  = self.playlist.pop(0)


    def play(self):
        self.get_playlist()
        for song in self.playlist:
            subprocess.call('mplayer ' + song['url'] + ' >/dev/null 2>&1', shell=True)

    def rate_music(self):
        post_data = self.login_data.copy()
        post_data['type'] = 'r'
        post_data['sid'] = self.playingsong['sid']
        s = requests.get('http://www.douban.com/j/app/radio/people?' + urllib.urlencode(post_data))


    def unrate_music(self):
        post_data = self.login_data.copy()
        post_data['type'] = 'u'
        post_data['sid'] = self.playingsong['sid']
        s = requests.get('http://www.douban.com/j/app/radio/people?' + urllib.urlencode(post_data))

if __name__ == '__main__':
    main()

############################################################################
