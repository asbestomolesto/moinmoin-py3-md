# -*- coding: iso-8859-1 -*-
"""
MoinMoin - make a test wiki

Usage:

    maketestwiki.py

@copyright: 2005 by Thomas Waldmann
@license: GNU GPL, see COPYING for details.
"""

import os, sys, shutil, errno
import tarfile

filename = globals().get("__file__") or sys.argv[0]
moinpath = os.path.abspath(os.path.join(os.path.dirname(filename), os.pardir, os.pardir))

WIKI = os.path.abspath(os.path.join(moinpath, 'tests', 'wiki'))
SHARE = os.path.abspath(os.path.join(moinpath, 'wiki'))


def removeTestWiki():
    print('removing old wiki ...')
    for dir in ['data', 'underlay']:
        try:
            shutil.rmtree(os.path.join(WIKI, dir))
        except OSError as err:
            if not (err.errno == errno.ENOENT or
                    (err.errno == 3 and os.name == 'nt')):
                raise


def copyData():
    print('copying data ...')
    src = os.path.join(SHARE, 'data')
    dst = os.path.join(WIKI, 'data')
    shutil.copytree(src, dst)


def untarUnderlay():
    # the full underlay (all help and system pages) is in tests/underlay.tar,
    # taken from the moin-1.9 repository (the release only ships the
    # LanguageSetup page with the language packs)
    tarname = os.path.join(moinpath, 'tests', 'underlay.tar')
    if not os.path.exists(tarname):
        tarname = os.path.join(SHARE, 'underlay.tar')
    if not os.path.exists(tarname):
        # released tarballs ship the underlay as a directory
        print('copying underlay ...')
        shutil.copytree(os.path.join(SHARE, 'underlay'), os.path.join(WIKI, 'underlay'))
        return
    print('untaring underlay ...')
    tar = tarfile.open(tarname)
    for member in tar:
        tar.extract(member, WIKI, filter='data')
    tar.close()


def run(skip_if_existing=False):
    try:
        os.makedirs(WIKI)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    if skip_if_existing and os.path.exists(os.path.join(WIKI, 'data')):
        return
    removeTestWiki()
    copyData()
    untarUnderlay()

if __name__ == '__main__':
    sys.path.insert(0, moinpath)
    run()

