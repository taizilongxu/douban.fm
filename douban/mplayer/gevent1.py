# -*- coding: utf-8 -*-

import gevent
from gevent.fileobject import FileObject
from subprocess import PIPE

from mplayer.core import Player
from mplayer import misc


__all__ = ['GeventPlayer']


class GeventPlayer(Player):
    """Player subclass with gevent integration.

    Mplayer's stdout and stderr are processed in seperate greenlets.
    This subclass is meant to be used with gevent-based applications.

    Shortcomings:
        - Class methods _generate_properties() and _generate_methods() use
          blocking pipe IO and may therefore starve other greenlets.
        - Method quit() calls wait() on the mplayer process, which will block
          the calling process until it exits. Note that quit() is called when
          the Player object is garbage collected.

    """

    def __init__(self, args=(), stdout=PIPE, stderr=None, autospawn=True):
        super(GeventPlayer, self).__init__(args, autospawn=False)
        self._stdout = _StdoutWrapper(handle=stdout)
        self._stderr = _StderrWrapper(handle=stderr, map=map)
        if autospawn:
            self.spawn()


class _StderrWrapper(misc._StderrWrapper):

    def _attach(self, source):
        super(_StderrWrapper, self)._attach(FileObject(source))
        gevent.spawn(self._greenlet_func)

    def _greenlet_func(self):
        while self._source is not None:
            self._process_output()


class _StdoutWrapper(_StderrWrapper, misc._StdoutWrapper):
    pass
