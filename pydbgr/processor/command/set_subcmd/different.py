# -*- coding: utf-8 -*-
#   Copyright (C) 2009 Rocky Bernstein
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#    02110-1301 USA.

from import_relative import *
# Our local modules
# FIXME: Until import_relative is fixed up...
import_relative('processor', '....', 'pydbgr')
Mbase_subcmd = import_relative('base_subcmd', '..', 'pydbgr')

class SetDifferent(Mbase_subcmd.DebuggerSetBoolSubcommand):
    """Set consecutive stops must be on different file/line positions.

By default, the debugger traces all events possible including line,
exceptions, call and return events. Just this alone may mean that for
any given source line several consecutive stops at a given line may
occur. Independent of this, Python allows one to put several commands
in a single source line of code. When a programmer does this, it might
be because the programmer thinks of the line as one unit.

One of the challenges of debugging is getting the granualarity of
stepping comfortable. Because of the above, stepping all events can
often be too fine-grained and annoying. By setting different on you
can set a more coarse-level of stepping which often still is small
enough that you won't miss anything important.

Note that the 'step' and 'next' debugger commands have '+' and '-'
suffixes if you wan to override this setting on a per-command basis.

See also 'set trace' to change what events you want to filter.
"""
    in_list    = True
    min_abbrev = len('dif')    # Min is "set dif"
    pass


