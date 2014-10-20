##douban.fm [![version](https://pypip.in/version/douban.fm/badge.svg)](https://pypi.python.org/pypi/douban.fm) [![Downloads](https://pypip.in/download/douban.fm/badge.png)](https://pypi.python.org/pypi/douban.fm)


ubuntu 14.04通过测试,其他平台暂时未做测试.其他平台可能需要在字符输入上做调整,欢迎PR.

这个版本的命令行界面是参考了 Node.js版本的[douban.fm](https://github.com/turingou/douban.fm)制作的,向原作者致敬.终端界面设计的非常好看.

Python版本

![screenshot](https://raw.githubusercontent.com/taizilongxu/douban.fm/master/img/2.png)

###Do something cool!

其实Node.js版本已经很好了,功能齐全,但是我发现在我的zsh + tmux环境下颜色竟然显示不出来,感觉很蛋疼.

###Download

    $ sudo pip install douban.fm

需要mplayer播放器依赖,如未安装:

    $ sudo apt-get install mplayer

###Usage

在终端下直接输入

    $ douban.fm

###Login

第一次登陆需要输入账号,密码,程序不会保留密码,而是保存返回的token存储在~/.douban_token.txt,下次登陆无需输入密码.

###Keys

支持vim按键

```
 [j]     --> 下
 [k]     --> 上
 [space] --> 播放
 [l]     --> 打开歌曲主页
 [g]     --> 移到最顶
 [G]     --> 移到最底
 [n]     --> 下一首
 [r]     --> 喜欢/取消喜欢
 [b]     --> 不再播放
 [q]     --> 退出
```

###Config(v0.2.8)

.doubanfm_config保存在了~/.doubanfm_config,根据需要可以修改按键的映射

```
[key]
UP = k       # 上
DOWN = j     # 下
TOP = g      # 顶
BOTTOM = G   # 底
OPENURL = l  # 打开歌曲主页
RATE = r     # 标记喜欢/取消喜欢
NEXT = n     # 下一首
BYE = b      # 不再播放
QUIT = q     # 退出
```

###Done

* 登陆token
* 显示PRO
* cli设计
* 播放,下一首,红心,不再播放
* 进度条(时间)
* 终端高度的自动调整
* pro用户歌曲kbps的选择(pro用户会自动选择192kbps)
* 歌曲结束request(发送歌曲完成)
* kbps的选择
* config设置

###TODO

* 歌曲暂停
* 播放歌曲数 红心数 不再播放数
* 歌词(歌词暂时没有好的API)
* 异常处理

###BUG

* ~~播放歌曲中有时候会暂停~~
* ~~退出后终端光标会隐藏~~

###参考资料

* Node.js版本的[douban.fm](https://github.com/turingou/douban.fm)
* [豆瓣电台 API](https://github.com/zonyitoo/doubanfm-qt/wiki/%E8%B1%86%E7%93%A3FM-API)

###License (MIT)
Copyright (c) 2014 hackerxu

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
