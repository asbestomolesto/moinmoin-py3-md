# -*- coding: iso-8859-1 -*-
# MoinMoin 1.10.0 (Python 3 port): converted to Python 3 (2to3) in 2026 by
# Claude (Anthropic AI) for Gabriele 'asbesto' Zaverio.
"""
    Outputs the text verbatimly.

    @copyright: 2005 MoinMoin:ThomasWaldmann
    @license: GNU GPL, see COPYING for details
"""

Dependencies = []

def macro_Verbatim(macro, text=''):
    return macro.formatter.escapedText(text)
