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

from subprocess import PIPE

import gtk
import gobject

from mplayer.core import Player
from mplayer import misc


__all__ = ['GPlayer', 'GtkPlayerView']


class GPlayer(Player):
    """Player subclass with GTK/GObject integration.

    The GTK/GObject main loop is used for processing the data in
    MPlayer's stdout and stderr. This subclass is meant to be used
    with GTK/GObject-based applications.

    """

    def __init__(self, args=(), stdout=PIPE, stderr=None, autospawn=True):
        super(GPlayer, self).__init__(args, autospawn=False)
        # Use the wrappers with GObject/GTK integration (defined below)
        self._stdout = _StdoutWrapper(handle=stdout)
        self._stderr = _StderrWrapper(handle=stderr)
        if autospawn:
            self.spawn()


class GtkPlayerView(gtk.Socket):
    """GTK widget which embeds MPlayer.

    This widget uses GPlayer internally and exposes it via the
    GtkPlayerView.player property.

    """

    __gsignals__ = {
        'eof': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_INT, ))
    }

    def __init__(self, args=(), stderr=None):
        """Arguments:

        args -- additional MPlayer arguments (default: ())
        stderr -- handle for MPlayer's stderr (default: None)

        """
        super(GtkPlayerView, self).__init__()
        self._player = GPlayer(('-msglevel', 'global=6', '-fixed-vo', '-fs') + args,
                               stderr=stderr, autospawn=False)
        self._player.stdout.connect(self._handle_data)
        self.connect('destroy', self._on_destroy)
        self.connect('hierarchy-changed', self._on_hierarchy_changed)

    @property
    def player(self):
        """GPlayer instance"""
        return self._player

    def _on_hierarchy_changed(self, *args):
        if self.parent is not None:
            self._player.args += ('-wid', self.get_id())
            self._player.spawn()
        else:
            self._on_destroy()

    def _on_destroy(self, *args):
        self._player.quit()

    def _handle_data(self, data):
        if data.startswith('EOF code:'):
            code = data.partition(':')[2].strip()
            self.emit('eof', int(code))


class _StderrWrapper(misc._StderrWrapper):

    def __init__(self, **kwargs):
        super(_StderrWrapper, self).__init__(**kwargs)
        self._tag = None

    def _attach(self, source):
        super(_StderrWrapper, self)._attach(source)
        self._tag = gobject.io_add_watch(self._source, gobject.IO_IN |
            gobject.IO_PRI | gobject.IO_HUP, self._process_output)

    def _detach(self):
        gobject.source_remove(self._tag)
        super(_StderrWrapper, self)._detach()


class _StdoutWrapper(_StderrWrapper, misc._StdoutWrapper):
    pass


# Register PyGTK type
gobject.type_register(GtkPlayerView)


if __name__ == '__main__':
    import sys

    w = gtk.Window()
    w.set_size_request(640, 480)
    w.set_title('GtkPlayer')
    w.connect('destroy', gtk.main_quit)
    v = GtkPlayerView()
    v.connect('eof', gtk.main_quit)
    w.add(v)
    w.show_all()
    v.player.loadfile(sys.argv[1])
    gtk.main()
