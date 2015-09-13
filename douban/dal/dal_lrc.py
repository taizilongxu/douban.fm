#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from dal_main import MainDal


class LrcDal(MainDal):

    def __init__(self, data):
        super(LrcDal, self).__init__(data)
        self.lrc = data.lrc

    @property
    def lines(self):
        return [line[1] for line in self.sort_lrc_dict if line[1]]

    @property
    def sort_lrc_dict(self):
        return sorted(self.lrc.iteritems(), key=lambda x: x[0])
