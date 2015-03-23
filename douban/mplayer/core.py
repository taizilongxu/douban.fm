# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2011  Darwin M. Bautista <djclue917@gmail.com>
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

import shlex
import atexit
import weakref
import subprocess
from functools import partial
from threading import Thread
try:
    import queue
except ImportError:
    import Queue as queue

from mplayer import mtypes, misc


__all__ = ['Player', 'Step']


def _quit(player):
    try:
        player.quit()
    except ReferenceError:
        pass


class Step(object):
    """A vector which contains information about the step size and direction.

    This is meant to be used with property access to implement
    the 'step_property' command like so:

        p.fullscreen = Step()
        p.time_pos = Step(50, -1)

    """

    def __init__(self, value=0, direction=0):
        """Arguments:

        value -- specifies by how much to change a property (default: 0)
        direction -- specifies the direction of the step (default: 0)
                     the change will be negative if direction < 0

        """
        super(Step, self).__init__()
        if not isinstance(value, mtypes.FloatType.type):
            raise TypeError('expected float or int for value')
        if not isinstance(direction, mtypes.IntegerType.type):
            raise TypeError('expected int for direction')
        self._val = mtypes.FloatType.adapt(value)
        self._dir = mtypes.IntegerType.adapt(direction)


class Player(object):
    """The base wrapper for MPlayer.

    It exposes MPlayer commands and properties as Python methods and properties,
    respectively. threading.Thread objects are used for processing the data in
    MPlayer's stdout and stderr.

    Class attributes:
    cmd_prefix -- prefix for MPlayer commands (default: CmdPrefix.PAUSING_KEEP_FORCE)
    exec_path -- path to the MPlayer executable (default: 'mplayer')
    version -- version of the introspected MPlayer executable (default: None)

    """

    _base_args = ('-slave', '-idle', '-really-quiet', '-msglevel', 'global=4',
                  '-input', 'nodefault-bindings', '-noconfig', 'all')
    cmd_prefix = misc.CmdPrefix.PAUSING_KEEP_FORCE
    exec_path = 'mplayer'
    version = None

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

    def __repr__(self):
        if self.is_alive():
            status = 'with pid = {0}'.format(self._proc.pid)
        else:
            status = 'not running'
        return '<{0} {1}>'.format(self.__class__.__name__, status)

    @property
    def stdout(self):
        """stdout of the MPlayer process"""
        return self._stdout

    @property
    def stderr(self):
        """stderr of the MPlayer process"""
        return self._stderr

    @property
    def args(self):
        """tuple of additional MPlayer arguments"""
        return self._args[len(self._base_args):]

    @args.setter
    def args(self, args):
        # Assume that args is a string.
        try:
            args = shlex.split(args)
        except AttributeError:
            # Force all args to string
            args = map(str, args)
        self._args = self._base_args + tuple(args)

    def _propget(self, pname, ptype):
        res = self._run_command('get_property', pname)
        if res is not None:
            return ptype.convert(res)

    def _propset(self, value, pname, ptype, pmin, pmax):
        if not isinstance(value, Step):
            if not isinstance(value, ptype.type):
                raise TypeError('expected {0}'.format(ptype.name))
            if pmin is not None and value < pmin:
                raise ValueError('value must be at least {0}'.format(pmin))
            if pmax is not None and value > pmax:
                raise ValueError('value must be at most {0}'.format(pmax))
            self._run_command('set_property', pname, ptype.adapt(value))
        else:
            self._run_command('step_property', pname, value._val, value._dir)

    @staticmethod
    def _gen_propdoc(ptype, pmin, pmax, propset):
        doc = ['type: {0}'.format(ptype.name)]
        if propset is not None:
            if pmin is not None:
                doc.append('min: {0}'.format(pmin))
            if pmax is not None:
                doc.append('max: {0}'.format(pmax))
        else:
            doc.append('(read-only)')
        return '\n'.join(doc)

    @classmethod
    def _generate_properties(cls):
        # Properties that don't have pmin == pmax == None but are actually read-only
        read_only = ['length', 'pause', 'stream_end', 'stream_length',
            'stream_start', 'stream_time_pos']
        rename = {'pause': 'paused'}
        proc = subprocess.Popen([cls.exec_path, '-list-properties'],
                                bufsize=-1, stdout=subprocess.PIPE)
        # Try to get the version of this executable
        try:
            cls.version = proc.stdout.readline().decode('utf-8', 'ignore').split()[1]
        except IndexError:
            pass
        for line in proc.stdout:
            line = line.decode('utf-8', 'ignore').split()
            # All property names in -list-properties are in lowercase
            if not line or not line[0].islower():
                continue
            try:
                pname, ptype, pmin, pmax = line
            except ValueError:
                pname, ptype, ptype2, pmin, pmax = line
                ptype += ' ' + ptype2
            # Get the corresponding Python type and convert pmin and pmax
            ptype = mtypes.type_map[ptype]
            pmin = ptype.convert(pmin) if pmin != 'No' else None
            pmax = ptype.convert(pmax) if pmax != 'No' else None
            # Generate property fget
            propget = partial(cls._propget, pname=pname, ptype=ptype)
            # Most properties with pmin == pmax == None are read-only
            # except for 'sub_delay'
            if (pmin is None and pmax is None and pname != 'sub_delay') or \
               pname in read_only:
                propset = None
            else:
                # Min and max values don't make sense for FlagType
                if ptype is mtypes.FlagType:
                    pmin = pmax = None
                propset = partial(cls._propset, pname=pname, ptype=ptype,
                                  pmin=pmin, pmax=pmax)
            # Generate property doc
            propdoc = cls._gen_propdoc(ptype, pmin, pmax, propset)
            prop = property(propget, propset, doc=propdoc)
            # Rename some properties to avoid conflict
            if pname in rename:
                pname = rename[pname]
            # There shouldn't be any naming conflict with hardcoded properties,
            # methods, class attributes, etc.
            assert not hasattr(cls, pname), "name conflict for '{0}'".format(pname)
            setattr(cls, pname, prop)

    @staticmethod
    def _process_args(req, types, *args):
        """Performs type checking and adaptation of arguments"""
        # Discard None only from optional args
        args = list(args[:req]) + [x for x in args[req:] if x is not None]
        for i, arg in enumerate(args):
            if not isinstance(arg, types[i].type):
                msg = 'expected {0} for argument {1}'.format(types[i].name, i + 1)
                raise TypeError(msg)
            args[i] = types[i].adapt(arg)
        return tuple(args)

    @staticmethod
    def _gen_method_func(name, args):
        sig = []
        types = []
        required = 0
        for i, arg in enumerate(args):
            if not arg.startswith('['):
                optional = ''
                required += 1
            else:
                arg = arg.strip('[]')
                optional = '=None'
            t = mtypes.type_map[arg]
            sig.append('{0}{1}{2}'.format(t.name, i, optional))
            types.append('mtypes.{0},'.format(t.__name__))
        sig = ','.join(sig)
        params = sig.replace('=None', '')
        types = ''.join(types)
        args = ', '.join(args)
        # As of now, there's no way of specifying a function's signature
        # without dynamically generating code
        code = '''
        def {name}(self, {sig}):
            """{name}({args})"""
            args = self._process_args({required}, ({types}), {params})
            return self._run_command('{name}', *args)
        '''.format(**locals())
        local = {}
        exec(code.strip(), globals(), local)
        return local[name]

    @classmethod
    def _generate_methods(cls):
        # Commands which have truncated names in -input cmdlist
        truncated = {'osd_show_property_te': 'osd_show_property_text'}
        proc = subprocess.Popen([cls.exec_path, '-input', 'cmdlist'],
                                bufsize=-1, stdout=subprocess.PIPE)
        for line in proc.stdout:
            # skip version string at end of mplayer2 output
            if line.startswith("MPlayer"):
                continue
            args = line.decode('utf-8', 'ignore').split()
            if not args:
                continue
            # Separate command name from command args
            name = args.pop(0)
            # Exclude conflicts with properties or defined attributes
            if hasattr(cls, name):
                continue
            # Exclude ALL get_* and *_property commands
            if name.startswith('get_') or name.endswith('_property'):
                continue
            # Fix truncated command names
            if name in truncated:
                name = truncated[name]
            func = cls._gen_method_func(name, args)
            setattr(cls, name, func)

    @classmethod
    def introspect(cls):
        """Introspect the MPlayer executable

        Generate available properties and methods based on the output of:
        $ mplayer -list-properties
        $ mplayer -input cmdlist

        See also http://www.mplayerhq.hu/DOCS/tech/slave.txt

        """
        if cls.version is None:
            cls._generate_properties()
            cls._generate_methods()

    def spawn(self):
        """Spawn the underlying MPlayer process."""
        if self.is_alive():
            return
        args = [self.exec_path]
        args.extend(self._args)
        # Start the MPlayer process (unbuffered)
        self._proc = subprocess.Popen(args, stdin=subprocess.PIPE,
            stdout=self._stdout._handle, stderr=self._stderr._handle,
            close_fds=(not subprocess.mswindows))
        if self._proc.stdout is not None:
            self._stdout._attach(self._proc.stdout)
        if self._proc.stderr is not None:
            self._stderr._attach(self._proc.stderr)

    def quit(self, retcode=0):
        """Terminate the underlying MPlayer process.
        Returns the exit status of MPlayer or None if not running.

        """
        if not isinstance(retcode, mtypes.IntegerType.type):
            raise TypeError('expected int for retcode')
        if not self.is_alive():
            return
        if self._proc.stdout is not None:
            self._stdout._detach()
        if self._proc.stderr is not None:
            self._stderr._detach()
        self._run_command('quit', mtypes.IntegerType.adapt(retcode))
        return self._proc.wait()

    def is_alive(self):
        """Check if MPlayer process is alive.
        Returns True if alive, else, returns False.

        """
        if self._proc is not None:
            return (self._proc.poll() is None)
        else:
            return False

    def _run_command(self, name, *args):
        """Send a command to MPlayer. The result, if any, is returned.
        args is assumed to be a tuple of strings.

        """
        if not self.is_alive():
            return
        cmd = [self.cmd_prefix, name]
        cmd.extend(args)
        cmd.append('\n')
        # Don't prefix the following commands
        if name in ['quit', 'pause', 'stop']:
            cmd.pop(0)
        cmd = ' '.join(cmd)
        # In Py3k, TypeErrors will be raised because cmd is a string but stdin
        # expects bytes. In Python 2.x on the other hand, UnicodeEncodeErrors
        # will be raised if cmd is unicode. In both cases, encoding the string
        # will fix the problem.
        try:
            self._proc.stdin.write(cmd)
        except (TypeError, UnicodeEncodeError):
            self._proc.stdin.write(cmd.encode('utf-8', 'ignore'))
        self._proc.stdin.flush()
        # Expect a response for 'get_property' only
        if name == 'get_property' and self._proc.stdout is not None:
            # The reponses for properties start with 'ANS_<property name>='
            key = 'ANS_{0}='.format(args[0])
            while True:
                try:
                    res = self._stdout._answers.get(timeout=1.0)
                except queue.Empty:
                    return
                if res.startswith(key):
                    break
                if res.startswith('ANS_ERROR='):
                    return
            ans = res.partition('=')[2].strip('\'"')
            if ans == '(null)':
                ans = None
            return ans


class _StderrWrapper(misc._StderrWrapper):

    def _attach(self, source):
        super(_StderrWrapper, self)._attach(source)
        t = Thread(target=self._thread_func)
        t.daemon = True
        t.start()

    def _thread_func(self):
        while self._source is not None:
            self._process_output()


class _StdoutWrapper(_StderrWrapper, misc._StdoutWrapper):
    pass


# Introspect on module load
try:
    Player.introspect()
except OSError:
    pass


if __name__ == '__main__':
    import sys

    def log(data):
        print('LOG: {0}'.format(data))

    def error(data):
        print('ERROR: {0}'.format(data))

    player = Player(sys.argv[1:], stderr=subprocess.PIPE)
    player.stdout.connect(log)
    player.stderr.connect(error)
    # block execution
    try:
        raw_input()
    except NameError: # raw_input() was renamed to input() in Python 3
        input()
