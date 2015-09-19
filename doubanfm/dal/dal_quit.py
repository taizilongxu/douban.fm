#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from doubanfm.dal.dal_main import MainDal
from termcolor import colored


class QuitDal(MainDal):

    def __init__(self, data):
        super(QuitDal, self).__init__(data)

    @property
    def info(self):
        return colored("  (╭￣3￣)╭♡ ", 'red') + colored("Quit(q)?", 'green')
