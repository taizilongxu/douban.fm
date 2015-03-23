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

from PyQt4 import QtCore, QtGui
# Use QX11EmbedContainer for OSes with X11 support (e.g. Linux)
# and Qwidget for Windows
try:
    from PyQt4.QtGui import QX11EmbedContainer as _Container
except ImportError:
    from PyQt4.QtGui import QWidget as _Container

from mplayer.core import Player
from mplayer import misc


__all__ = ['QtPlayer', 'QPlayerView']


class QtPlayer(Player):
    """Player subclass with Qt integration.

    The Qt event loop is used for processing the data in MPlayer's stdout
    and stderr. This subclass is meant to be used with Qt-based applications.

    """

    def __init__(self, args=(), stdout=PIPE, stderr=None, autospawn=True):
        super(QtPlayer, self).__init__(args, autospawn=False)
        # Use the wrappers with Qt integration (defined below)
        self._stdout = _StdoutWrapper(handle=stdout)
        self._stderr = _StderrWrapper(handle=stderr)
        if autospawn:
            self.spawn()


class QPlayerView(_Container):
    """Qt widget which embeds MPlayer.

    This widget uses QtPlayer internally and exposes it via the
    QPlayerView.player property.

    """

    eof = QtCore.pyqtSignal(int)

    def __init__(self, parent=None, args=(), stderr=None):
        """Arguments:

        parent -- the 'parent' argument of Qt classes (default: None)
        args -- additional MPlayer arguments (default: ())
        stderr -- handle for MPlayer's stderr (default: None)

        """
        super(QPlayerView, self).__init__(parent)
        self._player = QtPlayer(('-msglevel', 'global=6', '-fixed-vo', '-fs',
                                 '-wid', int(self.winId())) + args, stderr=stderr)
        self._player.stdout.connect(self._handle_data)
        self.destroyed.connect(self._on_destroy)

    @property
    def player(self):
        """QtPlayer instance"""
        return self._player

    def _on_destroy(self):
        self._player.quit()

    def _handle_data(self, data):
        if data.startswith('EOF code:'):
            code = data.partition(':')[2].strip()
            self.eof.emit(int(code))


class _StderrWrapper(misc._StderrWrapper):

    def __init__(self, **kwargs):
        super(_StderrWrapper, self).__init__(**kwargs)
        self._notifier = None

    def _attach(self, source):
        super(_StderrWrapper, self)._attach(source)
        self._notifier = QtCore.QSocketNotifier(self._source.fileno(),
            QtCore.QSocketNotifier.Read)
        self._notifier.activated.connect(self._process_output)

    def _detach(self):
        self._notifier.setEnabled(False)
        super(_StderrWrapper, self)._detach()


class _StdoutWrapper(_StderrWrapper, misc._StdoutWrapper):
    pass


if __name__ == '__main__':
    import sys

    app = QtGui.QApplication(sys.argv)
    w = QtGui.QWidget()
    w.resize(640, 480)
    w.setWindowTitle('QtPlayer')
    v = QPlayerView(w)
    v.eof.connect(app.closeAllWindows)
    v.resize(640, 480)
    w.show()
    v.player.loadfile(sys.argv[1])
    sys.exit(app.exec_())
