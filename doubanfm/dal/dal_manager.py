#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from doubanfm.dal.dal_main import MainDal
from doubanfm.colorset.colors import color_func  # colors


class ManagerDal(MainDal):

    def __init__(self, data):
        super(ManagerDal, self).__init__(data)
