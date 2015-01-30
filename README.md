##douban.fm [![version](https://pypip.in/version/douban.fm/badge.svg)](https://pypi.python.org/pypi/douban.fm) [![Downloads](https://pypip.in/download/douban.fm/badge.png)](https://pypi.python.org/pypi/douban.fm)


这个版本的命令行界面是参考了 Node.js版本的[douban.fm](https://github.com/turingou/douban.fm)制作的,向原作者致敬.终端界面设计的非常好看.

=======

感谢[Cloverstd](https://github.com/cloverstd)的修改,已经支持Mac OS X(>=V0.2.9)

PS:如果喜欢请加Star(*^__^*)……,如果有任何建议,欢迎提issue

主页( test): http://hackerxu.com/pages/doubanfm/

### Screenshots

![screenshot](https://raw.githubusercontent.com/taizilongxu/douban.fm/master/img/out.gif)

### Lyric

新增歌词界面

![Lyric](img/5.png)

### Support

Linux/Mac OS X

### Do something cool!

其实Node.js版本已经很好了,功能齐全,但是我发现在我的zsh + tmux环境下颜色竟然显示不出来,感觉很蛋疼.

### Installation

    $ sudo pip install douban.fm

需要mplayer播放器依赖,如未安装:

Ubuntu:

    $ sudo apt-get install mplayer

OS X:

    $ brew install mplayer

### Update

    $ sudo pip install --upgrade douban.fm

### Usage

在终端下直接输入

    $ douban.fm

### Login

第一次登陆需要输入账号,密码,程序不会保留密码,而是保存返回的token存储在~/.douban_token.txt,下次登陆无需输入密码.

### Keys

支持vim按键

```
移动
 [j]     --> 下
 [k]     --> 上
 [g]     --> 移到最顶
 [G]     --> 移到最底
音乐
 [space] --> 播放
 [w]     --> 打开歌曲主页
 [n]     --> 下一首
 [r]     --> 喜欢/取消喜欢
 [b]     --> 不再播放
 [q]     --> 退出
 [p]     --> 暂停
 [l]     --> 单曲循环
音量(>=V0.2.9)
 [=]     --> 增
 [-]     --> 减
 [m]     --> 静音
歌词(>=v0.2.9)
 [o]     --> 显示歌词
 [q]     --> 退出歌词
帮助(>=v0.2.12)
 [h]     --> 查看快捷键
```

### Configuration(>=v0.2.8)

.doubanfm_config保存在了~/.doubanfm_config,根据需要可以修改按键的映射

```
[key]
UP = k       # 上
DOWN = j     # 下
TOP = g      # 顶
BOTTOM = G   # 底
OPENURL = w  # 打开歌曲主页
RATE = r     # 标记喜欢/取消喜欢
NEXT = n     # 下一首
BYE = b      # 不再播放
QUIT = q     # 退出
PAUSE = p    # 暂停
LOOP = l     # 单曲循环
MUTE = m     # 静音
LRC = o      # 歌词
HELP = h     # 查看帮助
```

### Developer

[Wiki](https://github.com/taizilongxu/douban.fm/wiki)

### Done

* 登陆token
* 显示PRO
* cli设计
* 播放,下一首,红心,不再播放
* 进度条(时间)
* 终端高度的自动调整
* pro用户歌曲kbps的选择(pro用户会自动选择192kbps)
* 歌曲结束request(发送歌曲完成)
* config设置
* 调节音量(amixer) + 标题中显示音量
* 歌词
* Ubuntu桌面通知 by [Fansion](https://github.com/Fansion) | MAC OS 桌面通知 by [Cloverstd](https://github.com/cloverstd)
* 支持MAC OS by [Cloverstd](https://github.com/cloverstd)
* 歌曲暂停 by [Cloverstd](https://github.com/cloverstd)
* 单曲播放 by [Cloverstd](https://github.com/cloverstd)

### TODO

* 默认频道
* 播放歌曲数 红心数 不再播放数
* 异常处理

### BUG

* 静音下自动切换歌曲 BUG
* ~~播放歌曲中有时候会暂停~~
* ~~退出后终端光标会隐藏~~
* ~~.douban_token.txt路径问题~~
* ~~登陆异常处理~~
* ~~静音后播放下一首会取消静音~~
* ~~歌词颜色显示与center方法的冲突致使歌词不能居中~~
* ~~歌曲播放中歌词显示的定位~~

### Authors

* [Fansion](https://github.com/Fansion)
* [Cloverstd](https://github.com/cloverstd)

### Reference

* Node.js版本的[douban.fm](https://github.com/turingou/douban.fm)
* [豆瓣FM命令行播放器(pyfm)](https://github.com/skyline75489/pyfm)
* [豆瓣电台 API](https://github.com/zonyitoo/doubanfm-qt/wiki/%E8%B1%86%E7%93%A3FM-API)

###Log

V0.2.13 增加help页面,修改声卡兼容问题,优化线程增加切歌速度

V0.2.12 歌词界面美化

V0.2.11 config兼容问题

V0.2.10 滚动歌词,单曲循环,暂停,静音

V0.2.9 支持歌词,支持Mac OS X

V0.2.8 增加config

### License (MIT)

Copyright (c) 2014 hackerxu
