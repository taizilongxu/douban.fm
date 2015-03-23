# -*- coding: utf-8 -*-
#
# Copyright (C) 2008-2011  Darwin M. Bautista <djclue917@gmail.com>
#
# This file is part of mplayer.py.
#
# mplayer.py is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# mplayer.py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with mplayer.py.  If not, see <http://www.gnu.org/licenses/>.

import weakref
import asyncore
from subprocess import PIPE

from mplayer.core import Player
from mplayer import misc


__all__ = ['AsyncPlayer']


class AsyncPlayer(Player):
    """Player subclass with asyncore integration.

    The asyncore polling functions are used for processing the data in
    MPlayer's stdout and stderr. This subclass is meant to be used with
    asyncore-based applications.

    """

    def __init__(self, args=(), stdout=PIPE, stderr=None, autospawn=True, map=None):
        """Additional arguments:

        map -- custom map to be used with asyncore
               (default: None; use the asyncore global map)

        """
        super(AsyncPlayer, self).__init__(args, autospawn=False)
        self._stdout = _StdoutWrapper(handle=stdout, map=map)
        self._stderr = _StderrWrapper(handle=stderr, map=map)
        if autospawn:
            self.spawn()


class _StderrWrapper(misc._StderrWrapper):

    def __init__(self, **kwargs):
        super(_StderrWrapper, self).__init__(**kwargs)
        self._map = kwargs['map']
        self._dispatcher = None

    def _attach(self, source):
        super(_StderrWrapper, self)._attach(source)
        self._dispatcher = weakref.proxy(_FileDispatcher(self))

    def _detach(self):
        self._dispatcher.close()
        super(_StderrWrapper, self)._detach()


class _StdoutWrapper(_StderrWrapper, misc._StdoutWrapper):
    pass


class _FileDispatcher(asyncore.file_dispatcher):

    def __init__(self, wrapper):
        asyncore.file_dispatcher.__init__(self, wrapper._source, wrapper._map)
        # Monkey patching: replace the handle_read_event() method
        # with wrapper._process_output()
        self.handle_read_event = wrapper._process_output

    def writable(self):
        return False


if __name__ == '__main__':
    import sys
    import time
    from threading import Thread

    player = AsyncPlayer(['-really-quiet', '-msglevel', 'global=6'] + sys.argv[1:], stderr=PIPE)

    # Called for every line read from stdout
    def handle_data(line):
        if not line.startswith('EOF code'):
            print('LOG: {0}'.format(line))
        else:
            player.quit()
    # Called for every line read from stderr
    def log_error(msg):
        print('ERROR: {0}'.format(msg))
    # Connect subscribers
    player.stdout.connect(handle_data)
    player.stderr.connect(log_error)

    # Print time_pos every 1.0 second, just to demonstrate multithreading
    def status(p):
        while p.is_alive():
            print('time_pos = {0}'.format(p.time_pos))
            time.sleep(1.0)
    t = Thread(target=status, args=(player,))
    t.daemon = True
    t.start()
    # Enter loop
    asyncore.loop()
