# -*- coding: utf-8 -*-

"""Lightweight and dynamic MPlayer wrapper with a Pythonic API

Classes:

Player -- provides a clean, Pythonic interface to MPlayer
CmdPrefix -- contains the prefixes that can be used with MPlayer commands
Step -- use with property access to implement the 'step_property' command

AsyncPlayer -- Player subclass with asyncore integration (POSIX only)
GPlayer -- Player subclass with GTK/GObject integration
GeventPlayer -- Player subclass with gevent integration
QtPlayer -- Player subclass with Qt integration

GtkPlayerView -- provides a basic (as of now) PyGTK widget that embeds MPlayer
QPlayerView -- provides a PyQt4 widget similar to GtkPlayerView in functionality


Constants:

PIPE -- subprocess.PIPE, provided here for convenience
STDOUT -- subprocess.STDOUT, provided here for convenience
"""

__version__ = '0.7.0'
__author__ = 'Darwin M. Bautista <djclue917@gmail.com>'
__all__ = [
    'PIPE',
    'STDOUT',
    'Player',
    'CmdPrefix',
    'Step'
    ]

# Import here for convenience.
from subprocess import PIPE, STDOUT
from mplayer.core import Player, Step
from mplayer.misc import CmdPrefix
