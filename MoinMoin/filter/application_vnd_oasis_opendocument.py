# -*- coding: iso-8859-1 -*-
# MoinMoin 1.10.0 (Python 3 port): converted to Python 3 (2to3) in 2026 by
# Claude (Anthropic AI) for Gabriele 'asbesto' Zaverio.
"""
    MoinMoin - OpenOffice.org 2.0 *.od? Filter (OpenDocument)

    Depends on: nothing (only python with zlib)

    @copyright: 2006-2009 MoinMoin:ThomasWaldmann
    @license: GNU GPL, see COPYING for details.
"""

import re, zipfile

from MoinMoin import log
logging = log.getLogger(__name__)

rx_stripxml = re.compile("<[^>]*?>", re.DOTALL|re.MULTILINE)

def execute(indexobj, filename):
    try:
        zf = zipfile.ZipFile(filename, "r")
        data = zf.read("content.xml")
        zf.close()
        data = " ".join(rx_stripxml.sub(" ", data).split())
    except (zipfile.BadZipfile, RuntimeError) as err:
        logging.error("%s [%s]" % (str(err), filename))
        data = ""
    try:
        data = data.decode('utf-8')
    except UnicodeDecodeError:
        # protected with password? no valid OpenDocument file?
        data = ''
    return data

