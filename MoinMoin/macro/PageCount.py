# -*- coding: iso-8859-1 -*-
# MoinMoin 1.10.0 (Python 3 port): converted to Python 3 (2to3) in 2026 by
# Claude (Anthropic AI) for Gabriele 'asbesto' Zaverio.
"""
    Outputs the page count of the wiki.

    @copyright: 2007 MoinMoin:ThomasWaldmann
    @license: GNU GPL, see COPYING for details
"""

Dependencies = ['namespace']

from MoinMoin import wikiutil

def macro_PageCount(macro, exists=None):
    """ Return number of pages readable by current user

    Return either an exact count (slow!) or fast count including deleted pages.

    TODO: make macro syntax more sane
    """
    request = macro.request
    exists = wikiutil.get_unicode(request, exists, 'exists')
    # Check input
    only_existing = False
    if exists == 'exists':
        only_existing = True
    elif exists:
        raise ValueError("Wrong argument: %r" % exists)

    count = request.rootpage.getPageCount(exists=only_existing)
    return macro.formatter.text("%d" % count)

