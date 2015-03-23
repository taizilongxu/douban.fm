# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2011  Darwin M. Bautista <djclue917@gmail.com>
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

try:
    import queue
except ImportError:
    import Queue as queue


__all__ = ['CmdPrefix']


class CmdPrefix(object):
    """MPlayer command prefixes"""

    PAUSING = 'pausing'
    PAUSING_TOGGLE = 'pausing_toggle'
    PAUSING_KEEP = 'pausing_keep'
    PAUSING_KEEP_FORCE = 'pausing_keep_force'


class _StderrWrapper(object):

    def __init__(self, **kwargs):
        super(_StderrWrapper, self).__init__()
        self._handle = kwargs['handle']
        self._source = None
        self._subscribers = []

    def _attach(self, source):
        self._source = source

    def _detach(self):
        self._source = None

    def _process_output(self, *args):
        line = self._source.readline().decode('utf-8', 'ignore')
        if line:
            line = line.rstrip()
            if line:
                for subscriber in self._subscribers:
                    subscriber(line)
            return True
        else:
            # Automatically detach when MPlayer dies unexpectedly
            self._detach()
            return False

    def connect(self, subscriber):
        """Connect a subscriber to this publisher"""
        if not hasattr(subscriber, '__call__'):
            # Raise TypeError
            subscriber()
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)

    def disconnect(self, subscriber=None):
        """Disconnect one or all subscribers from this publisher"""
        if subscriber is None:
            self._subscribers = []
        elif subscriber in self._subscribers:
            self._subscribers.remove(subscriber)


class _StdoutWrapper(_StderrWrapper):

    def __init__(self, **kwargs):
        super(_StdoutWrapper, self).__init__(**kwargs)
        self._answers = None

    def _attach(self, source):
        super(_StdoutWrapper, self)._attach(source)
        self._answers = queue.Queue()

    def _process_output(self, *args):
        line = self._source.readline().decode('utf-8', 'ignore')
        if line:
            line = line.rstrip()
            if line.startswith('ANS_'):
                self._answers.put_nowait(line)
            elif line:
                for subscriber in self._subscribers:
                    subscriber(line)
            return True
        else:
            # Automatically detach when MPlayer dies unexpectedly
            self._detach()
            return False
