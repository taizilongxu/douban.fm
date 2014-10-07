##![](http://ww3.sinaimg.cn/large/61ff0de3gw1e77q7mth9dj200z00z3ya.jpg) Douban FM v0.1.7


ubuntu通过测试,其他平台暂时未做测试.

这个版本的命令行界面是参考了 Node.js版本的[douban.fm](https://github.com/turingou/douban.fm)制作的.

Node.js版本

![screenshot](http://ww1.sinaimg.cn/large/61ff0de3tw1ecij3dq80bj20m40ez75u.jpg)

Python版本

![screenshot](img/1.png)

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

###已完成功能

* 登陆token
* 显示PRO 暂时只支持最高128kbps
* cli设计
* 播放,下一首,红心,不再播放
* 进度条

###TODO

* 歌曲暂停
* 歌曲结束request(记录歌曲播放数)
* 播放歌曲数 红心数 不再播放数
* 歌词
* 终端高度的自动调整

###BUG

* ~~播放歌曲中有时候会暂停~~
* ~~退出后终端光标会隐藏~~

### MIT license
Copyright (c) 2013 turing &lt;i@guoyu.me&gt;

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the &quot;Software&quot;), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED &quot;AS IS&quot;, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

###参考资料

* Node.js版本的[douban.fm](https://github.com/turingou/douban.fm)
* [豆瓣电台 API](https://github.com/zonyitoo/doubanfm-qt/wiki/%E8%B1%86%E7%93%A3FM-API)
