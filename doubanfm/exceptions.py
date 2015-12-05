import os
import sys
from termcolor import colored


class GenericError(Exception):

    message = 'an error occurred'

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs

        if not message:
            message = self.message % kwargs

        super(GenericError, self).__init__(colored(message, 'red'))


class APIError(GenericError):
    pass


class ConfigError(GenericError):
    pass


class MplayerError(GenericError):
    message = "Mplayer error, check if install mplayer"


class Success(object):
    def __init__(self, s):
        print >>sys.stderr, "OK:\n", s


class Warn(object):
    def __init__(self, s):
        print >>sys.stderr, "WARN:\n", s


class Error(object):
    def __init__(self, s):
        print >>sys.stderr, "ERROR:\n", s


class Fatal(object):
    def __init__(self, s, code=111):
        print >>sys.stderr, "FATAL:\n", s
        sys.exit(code)
