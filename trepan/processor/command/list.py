# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2012-2017 Rocky Bernstein
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
import inspect, os, linecache, pyficache, sys

# Our local modules
from pygments.console import colorize

# Our local modules
from trepan.processor.command import base_cmd as Mbase_cmd
from trepan.processor.cmdlist import parse_list_cmd


class ListCommand(Mbase_cmd.DebuggerCommand):
    """**list**  *location*  [ **,** *number* ]
**list**  **,** *location* ]
**list**  **+** | **-**

List source code.

If a module or function is given listing centered around
that. *number* is given, that is used as the last number to list if it
is greater than the number in the linespec; otherwise it is used as a
count.

Without arguments, print lines centered around the current line.

If this is the first `list` command issued since the debugger command
loop was entered, then the current line is the current frame. If a
subsequent list command was issued with no intervening frame changing,
then that is start the line after we last one previously shown.

in addtion to the usual kinds of *location* you can also use:

  - a '.' for the location of the current frame
  - a '-' for the lines before the last list
  - a '+' for the lines after the last list

The last list location starts out at '.' or the current frame

If the location form is used with a subsequent parameter, the
parameter is the starting line number is used. When there two numbers
are given, the last number value is treated as a stopping line unless
it is less than the start line, in which case it is taken to mean the
number of lines to list instead.

Wherever a number is expected, it does not need to be a constant --
just something that evaluates to a positive integer.

Examples:
--------

    list 5              # List starting from line 5 of current file
    list 5 ,            # Same as above.
    list foo.py:5       # List starting from line 5 of file foo.py
    list foo()          # List starting from function foo
    list os.path:5      # List starting from line 5 of module os.path
    list os.path 5      # Same as above.
    list os.path 5 6    # list lines 5 and 6 of os.path
    list os.path 5 2    # Same as above, since 2 < 5.
    list foo.py:5 2     # List two lines starting from line 5 of file foo.py
    list os.path.join() # List lines around the os.join.path function.
    list .            # List lines centered from where we currently are stopped
    list -            # List lines previous to those just shown

See also:
---------

`set listize` or `show listsize` to see or set the value; `help syntax location`
for specification of a location.

    """

    aliases       = ('l',)
    category      = 'files'
    min_args      = 0
    max_args      = 3
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = False
    short_help    = 'List source code'

    def run(self, args):
        proc = self.proc
        dbg_obj  = self.core.debugger
        listsize = dbg_obj.settings['listsize']
        filename, first, last = parse_list_cmd(proc, args, listsize)
        curframe = proc.curframe
        if filename is None: return
        filename = pyficache.unmap_file(pyficache.pyc2py(filename))

        # We now have range information. Do the listing.
        max_line = pyficache.size(filename)
        if max_line is None:
            self.errmsg('No file %s found; using "deparse" command instead to show source' %
                        filename)
            proc.commands['deparse'].run(['deparse'])
            return

        canonic_filename = os.path.realpath(os.path.normcase(filename))

        if first > max_line:
            self.errmsg('Bad start line %d - file "%s" has only %d lines'
                        % (first, filename, max_line))
            return

        if last > max_line:
            self.msg('End position changed to last line %d ' % max_line)
            last = max_line

        bplist = self.core.bpmgr.bplist
        opts = {
            'reload_on_change' : self.settings['reload'],
            'output'           : self.settings['highlight'],
            'strip_nl'         : False,
            }

        if 'style' in self.settings:
            opts['style'] = self.settings['style']

        try:
            for lineno in range(first, last+1):
                line = pyficache.getline(filename, lineno, opts)
                if line is None:
                    line = linecache.getline(filename, lineno,
                                             proc.frame.f_globals)
                    pass
                if line is None:
                    self.msg('[EOF]')
                    break
                else:
                    line = line.rstrip('\n')
                    s = proc._saferepr(lineno).rjust(3)
                    if len(s) < 5: s += ' '
                    if (canonic_filename, lineno,) in list(bplist.keys()):
                        bp    = bplist[(canonic_filename, lineno,)][0]
                        a_pad = '%02d' % bp.number
                        s    += bp.icon_char()
                    else:
                        s    += ' '
                        a_pad = '  '
                        pass
                    if curframe and lineno == inspect.getlineno(curframe):
                        s += '->'
                        if 'plain' != self.settings['highlight']:
                            s = colorize('bold', s)
                    else:
                        s += a_pad
                        pass
                    self.msg(s + '\t' + line)
                    proc.list_lineno = lineno
                    pass
                pass
            pass
        except KeyboardInterrupt:
            pass
        return False

if __name__ == '__main__':

    def doit(cmd, args):
        proc = cmd.proc
        proc.current_command = ' '.join(args)
        cmd.run(args)


    from trepan.processor.command import mock as Mmock
    from trepan.processor.cmdproc import CommandProcessor
    d = Mmock.MockDebugger()
    cmdproc = CommandProcessor(d.core)
    cmdproc.frame = sys._getframe()
    cmdproc.setup()
    lcmd = ListCommand(cmdproc)

    print('--' * 10)
    # doit(lcmd, ['list'])

    # doit(lcmd, ['list', __file__ + ':10'])
    # print('--' * 10)

    # doit(lcmd, ['list', 'os:10'])
    # print('--' * 10)

    # doit(lcmd, ['list', '.'])
    # print('--' * 10)

    # doit(lcmd, ['list', '10'])
    # print('--' * 10)

    # doit(lcmd, ['list', '1000'])

    def foo():
        return 'bar'
    # doit(lcmd, ['list', 'foo()'])
    # print('--' * 10)
    # doit(lcmd, ['list'])
    # print('--' * 10)
    # doit(lcmd, ['list', '-'])
    # doit(lcmd, ['list', '-'])
    # doit(lcmd, ['list', '+'])
    # doit(lcmd, ['list', '+'])
    doit(lcmd, ['list', '40', '60'])
    # doit(lcmd, ['list', '20', '5'])

    # doit(lcmd, ['list', 'os.path'])
    # print('--' * 10)
    # doit(lcmd, ['list', 'os.path', '15'])
    # print('--' * 10)
    # doit(lcmd, ['list', 'os.path', '30', '3'])
    # print('--' * 10)
    # doit(lcmd, ['list', 'os.path', '40', '50'])
    # print('--' * 10)

    # doit(lcmd, ['list', os.path.abspath(__file__)+':3', '4'])
    # print('--' * 10)
    # doit(lcmd, ['list', os.path.abspath(__file__)+':3', '12-10'])
    # doit(lcmd, ['list', 'os.path:5'])
    pass
