#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
歌词解析, 把歌词解析成字典形式
reference: (http://reverland.org/python/2014/10/09/lrc/)
"""
import re


def lrc2dict(lrc):
    def remove(x):
        return x.strip('[|]')

    lrc_dict = {}
    for line in lrc.split('\n'):
        if line.strip('\n'):
            time_stamps = re.findall(r'\[[^\]]+\]', line)
            if time_stamps:
                # 截取歌词
                lyric = line
                for tplus in time_stamps:
                    lyric = lyric.replace(tplus, '')
                # 解析时间
                for tplus in time_stamps:
                    t = remove(tplus)
                    tag_flag = t.split(':')[0]
                    # 跳过: [ar: 逃跑计划]
                    if not tag_flag.isdigit():
                        continue
                    # 时间累加
                    time_lrc = int(tag_flag) * 60
                    time_lrc += int(t.split(':')[1].split('.')[0])
                    lrc_dict[time_lrc] = lyric
    return lrc_dict


def main():
    with open('3443588.lrc', 'r') as F:
        lrc = F.read()
    lrc_dict = lrc2dict(lrc)
    for key in lrc_dict:
        print key, lrc_dict[key]

if __name__ == '__main__':
    main()
