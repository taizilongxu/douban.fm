#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from doubanfm.dal.dal_main import MainDal


class LrcDal(MainDal):

    def __init__(self, data, offset):
        super(LrcDal, self).__init__(data)
        self.lrc = data.lrc
        self.lrc_offset = offset

    @property
    def lines(self):
        return [line[1] for line in self.sort_lrc_dict if line[1]]

    @property
    def sort_lrc_dict(self):
        return sorted(self.lrc.iteritems(), key=lambda x: x[0])

    @property
    def title(self):
        if self.lrc_offset != 0:
            title_offset = '+' if self.lrc_offset > 0 else ''
            title_offset += str(self.lrc_offset) + 's'
        else:
            title_offset = ''
        return super(LrcDal, self).title + ' ' + title_offset
