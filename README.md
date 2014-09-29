##Douban FM v0.1.0

目前只支持linux,其他平台暂时未做测试,但是只要满足python2.7理论上就可以运行

这个版本是基于 node.js版本的[douban.fm](https://github.com/turingou/douban.fm)制作的,因为自己不熟悉node.js,所以做了个python版本,而且python版本需要安装的依赖更少,尚有部分功能还未添加.


![](img/1.png)


###依赖

需要mplayer播放器依赖,如未安装:

    sudo apt-get install mplayer

###按键

支持vim按键

* j 下
* k 上
* g 移到最顶
* G 移到最底
* n 下一首
* r 喜欢/取消喜欢
* b 不再播放
* space 播放歌曲

###已完成功能

* 登陆token
* PRO
* cli设计
* 播放,下一首,红心,不再播放

###TODO

* 进度条
* 歌词
* 连续操作会产生字符在终端输出的bug
