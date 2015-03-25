#!/usr/bin/env python
# encoding: utf-8
import subprocess
from threading import Thread
import Queue
import time
import select
<<<<<<< HEAD
import logging

logger = logging.getLogger()
=======
import logger

logger = logger.log
>>>>>>> 0def3c2202dba59aad9abcc38c78bc738d805ba5

class Player(object):

    # _base_args = ['-slave', '-really-quiet',\
    #                 '-input', 'nodefault-bindings', '-noconfig', 'all']
    _cmd = ['mplayer', '-slave', '-nolirc', '-quiet', '-softvol',\
            '-cache', '5120', '-cache-min', '1']
    cmd_prefix = ''

    def __init__(self, autospawn=False):
        """Arguments:
        """
        # print self.args
        self._proc = None
        # Terminate the MPlayer process when Python terminates
        if autospawn:
            self.spawn()

    def spawn(self, url=''):
        """Spawn the underlying MPlayer process."""
        self.args = self._cmd + [url.replace('\\', '')]
        if self.is_alive():
            self.quit()
        # Start the MPlayer process
        self._proc = subprocess.Popen(self.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)

    # def __del__(self):
    #     # Terminate the MPlayer process when instance is about to be destroyed
    #     if self.is_alive():
    #         self.quit()

    def __repr__(self):
        if self.is_alive():
            status = 'with pid = {0}'.format(self._proc.pid)
        else:
            status = 'not running'
        return '<{0} {1}>'.format(self.__class__.__name__, status)

    def is_alive(self):
        if self._proc is not None:
            if self._proc.poll() is None:
                return True
            else:
                return False
        else:
            return False

    def quit(self):
        if self._proc:
            self._proc.kill()

    @property
    def time_pos(self):
        songtime = self._run_command('get_time_pos', 'ANS_TIME_POSITION')
        if songtime:
            return int(round(float(songtime)))

    def set_volume(self, num):
        """the num is int and return nothing"""
        self._run_command('volume {0} 1'.format(num))

    def set_pause(self):
        self._run_command('pause')


    def _run_command(self, cmd, expect=None):
        """Send a command to MPlayer. The result, if any, is returned.
        args is assumed to be a tuple of strings.
        """
        if not self.is_alive():
            return
        cmd = [self.cmd_prefix, cmd]
        cmd.append('\n')
        # Don't prefix the following commands
        if cmd in ['quit', 'pause', 'stop']:
            cmd.pop(0)
        cmd = ' '.join(cmd)
        logger.debug(cmd)
        # In Py3k, TypeErrors will be raised because cmd is a string but stdin
        # expects bytes. In Python 2.x on the other hand, UnicodeEncodeErrors
        # will be raised if cmd is unicode. In both cases, encoding the string
        # will fix the problem.
        try:
            self._proc.stdin.write(cmd)
        except (TypeError, UnicodeEncodeError):
            self._proc.stdin.write(cmd.encode('utf-8', 'ignore'))
        # self._proc.stdin.flush()
        # Expect a response for 'get_property' only
        if expect:
            while select.select([self._proc.stdout], [], [], 0.01)[0]:
                # The reponses for properties start with 'ANS_<property name>='
                output = self._proc.stdout.readline()
                split_output = output.split(expect + '=', 1)
                if len(split_output) == 2 and split_output[0] == '': # we have found it
                    value = split_output[1]
                    return value.rstrip()
        return


def main():
    player = Player('http://mr3.douban.com/201308250247/4a3de2e8016b5d659821ec76e6a2f35d/view/song/small/p1562725.mp3')
    # print player._run_command('get_time_pos')
    time.sleep(4)
    print player.time_pos

if __name__ == '__main__':
    main()
