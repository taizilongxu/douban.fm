import subprocess
from threading import Thread

def _quit(player):
    try:
        player.quit()
    except ReferenceError:
        pass

class Player(object):

    _base_args = ('-slave', '-idle', '-really-quiet', '-msglevel', 'global=4',
                              '-input', 'nodefault-bindings', '-noconfig', 'all')
    exec_path = 'mplayer'

    def __init__(self, args=(), stdout=subprocess.PIPE, stderr=None, autospawn=True):
        """Arguments:
        args -- additional MPlayer arguments (default: ())
        stdout -- handle for MPlayer's stdout (default: subprocess.PIPE)
        stderr -- handle for MPlayer's stderr (default: None)
        autospawn -- call spawn() after instantiation (default: True)
        """
        super(Player, self).__init__()
        self.args = args
        self._stdout = _StdoutWrapper(handle=stdout)
        self._stderr = _StderrWrapper(handle=stderr)
        self._proc = None
        # Terminate the MPlayer process when Python terminates
        atexit.register(_quit, weakref.proxy(self))
        if autospawn:
            self.spawn()

    def __del__(self):
        # Terminate the MPlayer process when instance is about to be destroyed
        if self.is_alive():
            self.quit()
