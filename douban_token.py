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
        # 红心兆赫需要手动添加
        self.channels = [{
            'name':'红心兆赫',
            'channel_id' : -3
            }]
        # pro用户
        self.pro = 0
        self.playlist = []
        self.playingsong = {}
        self.login()
        self.get_channels()
        # 查看是否是pro用户
        self.is_pro()

    def is_pro(self):
        self.get_playlist()
        self.get_song()
        if not int(self.playingsong['kbps']) == 64:
            self.pro = 1

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

    def play_next(self):
        post_data = self.login_data.copy()

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

# user_id, user_name, expire, token = login()
# get_channel()
# channel = 1
# get_playlist(channel,user_id, expire, token)

def main():
    douban = Doubanfm('','')
    print douban.user_name

    # while True:
    douban.get_playlist()
    print douban.login_data

if __name__ == '__main__':
    main()

############################################################################
