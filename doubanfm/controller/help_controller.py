#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import logging

from doubanfm.views import help_view
from doubanfm.controller.lrc_controller import LrcController

logger = logging.getLogger('doubanfm')  # get logger


class HelpController(LrcController):
    """
    按键控制
    """

    def __init__(self, player, data):
        # 接受player, data, view
        super(HelpController, self).__init__(player, data)
        self.view = help_view.Help(self.data)
