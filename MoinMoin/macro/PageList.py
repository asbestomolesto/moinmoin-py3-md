# -*- coding: iso-8859-1 -*-
# MoinMoin 1.10.0 (Python 3 port): converted to Python 3 (2to3) in 2026 by
# Claude (Anthropic AI) for Gabriele 'asbesto' Zaverio.
"""
    MoinMoin - PageList

    print a list of pages whose title matches the search term

    @copyright: @copyright: 2001-2003 Juergen Hermann <jh@web.de>,
                2003-2008 MoinMoin:ThomasWaldmann
                2008 MoinMoin:ReimarBauer
    @license: GNU GPL, see COPYING for details.
"""

Dependencies = ["namespace"]
from MoinMoin import search, wikiutil
from MoinMoin.macro.FullSearch import execute as fs_execute

def execute(macro, args):
    _ = macro._
    case = 0

    # If called with empty or no argument, default to regex search for .+, the full page list.
    needle = wikiutil.get_unicode(macro.request, args, 'needle', 'regex:.+')

    return fs_execute(macro, needle, titlesearch=True, case=case)

