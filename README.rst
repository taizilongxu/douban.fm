##douban.fm  [![PyPI version](https://badge.fury.io/py/douban.fm.svg)](http://badge.fury.io/py/douban.fm)


ubuntu 14.04通过测试,其他平台暂时未做测试.

这个版本的命令行界面是参考了 Node.js版本的[douban.fm](https://github.com/turingou/douban.fm)制作的.

Python版本

![screenshot](https://raw.githubusercontent.com/taizilongxu/douban.fm/master/img/2.png)

###为什么Python版本

其实Node.js版本已经很好了,功能齐全,但是我发现在我的zsh + tmux环境下颜色竟然显示不出来,感觉很蛋疼.

###安装

    sudo pip install douban.fm

需要mplayer播放器依赖,如未安装:

    sudo apt-get install mplayer

###使用

在终端下直接输入douban.fm

###登陆

第一次登陆需要输入账号,密码,程序不会保留密码,而是保存返回的token存储在.douban_token.txt,下次登陆无需输入密码.

###按键

支持vim按键

* j 下
* k 上
* g 移到最顶
* G 移到最底
* n 下一首
* r 喜欢/取消喜欢
* b 不再播放
* space 播放
* q 退出

###已完成功能

* 登陆token
* 显示PRO
* cli设计
* 播放,下一首,红心,不再播放
* 进度条
* 终端高度的自动调整
* pro用户歌曲kbps的选择
* 歌曲结束request(发送歌曲完成)
* kbps的选择

###TODO

* 歌曲暂停
* 播放歌曲数 红心数 不再播放数
* 歌词

###BUG

* ~~播放歌曲中有时候会暂停~~
* ~~退出后终端光标会隐藏~~


###参考资料

* Node.js版本的[douban.fm](https://github.com/turingou/douban.fm)
* [豆瓣电台 API](https://github.com/zonyitoo/doubanfm-qt/wiki/%E8%B1%86%E7%93%A3FM-API)
