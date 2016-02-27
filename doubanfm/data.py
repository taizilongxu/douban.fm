import logging

from doubanfm.exceptions import Fatal

try:
    from doubanfm.config import db_config
except Exception, err:
    raise Fatal(err)

from doubanfm.model import Playlist, Channel
from doubanfm.colorset import theme

logger = logging.getLogger('doubanfm')


class Data(object):
    """
    集合所有数据, 并提供方法
    所有外部接口都只会调用这个类/方法
    """

    def __init__(self):
        self.playlist = Playlist()
        self.lines = Channel().lines
        # self.hitory = History()
        self.keys = db_config.keys  # keys
        self.volume = db_config.volume  # 声量
        self.theme_id = db_config.theme_id  # 主题id
        self.channel = db_config.channel  # 当前频道
        self.user_name = db_config.user_name  # 用户名

        self.netease = db_config.netease  # 网易高品质音乐
        self.song_like = False  # 当前歌词是否like
        self.pause = False  # 歌曲暂停
        self.loop = False  # 单曲循环
        self.pro = False  # pro用户
        self.mute = False  # 静音
        self.time = 0  # 时间/秒

    @property
    def theme(self):
        THEME = ['default', 'larapaste', 'monokai', 'tomorrow']
        return getattr(theme, THEME[self.theme_id])

    def set_theme_id(self, value):
        self.theme_id = value

    @property
    def lrc(self):
        return self.playlist.get_lrc()

    @property
    def playingsong(self):
        return self.playlist.get_playingsong()

    def bye(self):
        self.playlist.bye()

    def get_daily_song(self):
        return self.playlist.get_daily_song(self.netease)

    def get_song(self):
        playingsong = self.playlist.get_song(self.netease) if self.channel != 2 else self.get_daily_song()  # 位置2为每日推荐歌单
        self.song_like = True if str(playingsong['like']) == '1' else False
        return playingsong

    def set_channel(self, channel_index):
        self.playlist.set_channel(channel_index)

    def set_song_like(self, playingsong):
        self.playlist.set_song_like(playingsong)

    def set_song_unlike(self, playingsong):
        self.playlist.set_song_unlike(playingsong)

    def submit_music(self, playingsong):
        self.playlist.submit_music(playingsong)

    def change_volume(self, increment):
        """调整音量大小"""
        if increment == 1:
            self.volume += 5
        else:
            self.volume -= 5
        self.volume = max(min(self.volume, 100), 0)  # 限制在0-100之间

    def save(self):
        db_config.save_config(self.volume,
                              self.channel,
                              self.theme_id,
                              self.netease)
