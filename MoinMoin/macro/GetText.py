# -*- coding: iso-8859-1 -*-
# MoinMoin 1.10.0 (Python 3 port): converted to Python 3 (2to3) in 2026 by
# Claude (Anthropic AI) for Gabriele 'asbesto' Zaverio.
"""
    MoinMoin - Load I18N Text

    This macro has the main purpose of supporting Help* page authors
    to insert the texts that a user actually sees on his screen into
    the description of the related features (which otherwise could
    get very confusing).

    @copyright: 2001 Juergen Hermann <jh@web.de>
    @license: GNU GPL, see COPYING for details.
"""

Dependencies = ["language"]

def macro_GetText(macro, text=''):
    """ Return a translation of args, or args as is """
    translation = macro.request.getText(text)

    return macro.formatter.text(translation)

