#!/usr/bin/env python3
# MoinMoin 1.10.0 (Python 3 port): modified in 2026 by Claude (Anthropic AI)
# for Gabriele 'asbesto' Zaverio - see docs/CHANGES and the git history for details.
"""
    MoinMoin installer

    @copyright: 2001-2005 by Juergen Hermann <jh@web.de>,
                2006-2020 by MoinMoin:ThomasWaldmann
    @license: GNU GPL, see COPYING for details.

    Python 3 port: uses setuptools (distutils was removed in Python 3.12).
"""

import os, sys

from setuptools import setup, find_packages

# PEP 517 builds do not put the source directory into sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from MoinMoin.version import release, revision


#############################################################################
### Helpers
#############################################################################

def isbad(name):
    """ Whether name should not be installed """
    return (name.startswith('.') or
            name.startswith('#') or
            name.endswith('.pickle') or
            name.endswith('.pyc') or
            name in ('CVS', '__pycache__'))

def isgood(name):
    """ Whether name should be installed """
    return not isbad(name)

def makeDataFiles(prefix, dir):
    """ Create data_files structure from dir

    All files rooted under dir are copied into prefix, excluding dir itself:
        makeDataFiles('prefix', 'root') creates
        [('prefix', ['root/file1', 'root/file2']),
         ('prefix/dir', ['root/dir/file']), ...]
    """
    dir = dir.rstrip('/')
    strip = len(dir) + 1
    found = []
    for dirname, dirnames, filenames in os.walk(dir):
        dirnames[:] = sorted(d for d in dirnames if isgood(d))
        files = [os.path.join(dirname, name) for name in sorted(filenames) if isgood(name)]
        found.append((os.path.join(prefix, dirname[strip:]).rstrip('/'), files))
    return found

def make_filelist(dir, strip_prefix=''):
    """ list of all FILES below dir, stripping off strip_prefix at the left side
        (package_data globs must not match directories)
    """
    found = []
    for dirname, dirnames, filenames in os.walk(dir):
        dirnames[:] = [d for d in dirnames if isgood(d)]
        for name in filenames:
            if isgood(name):
                path = os.path.join(dirname, name)
                if path.startswith(strip_prefix):
                    path = path[len(strip_prefix):]
                found.append(path)
    return sorted(found)


#############################################################################
### Call setup()
#############################################################################

setup_args = {
    'name': "moin",
    'version': release,
    'description': "MoinMoin %s is an easy to use, full-featured and extensible wiki software package (Python 3 port)" % (release, ),
    'author': "Juergen Hermann et al.",
    'author_email': "moin-user@python.org",
    # MoinMoin 1.10.0, the Python 3 port, made with the assistance of Claude (Anthropic AI)
    'maintainer': "Gabriele 'asbesto' Zaverio",
    'maintainer_email': "aladarmrgradymezil@gmail.com",
    'url': "https://moinmo.in/",
    'license': "GNU GPL",
    'long_description': """
    MoinMoin is an easy to use, full-featured and extensible wiki software
    package written in Python. It can fulfill a wide range of roles, such as
    a personal notes organizer deployed on a laptop or home web server,
    a company knowledge base deployed on an intranet, or an Internet server
    open to individuals sharing the same interests, goals or projects.

    This is MoinMoin 1.10.0: MoinMoin 1.9.11 ported to Python 3. Wiki data, configuration
    and plugins of the 1.9 series stay compatible (plugins have to be
    ported to Python 3, too).""",
    'keywords': "wiki web",
    'platforms': "any",
    'classifiers': """Development Status :: 5 - Production/Stable
Environment :: No Input/Output (Daemon)
Environment :: Web Environment
Intended Audience :: System Administrators
Intended Audience :: End Users/Desktop
License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)
Operating System :: POSIX
Operating System :: POSIX :: Linux
Programming Language :: Python
Programming Language :: Python :: 3
Topic :: Internet :: WWW/HTTP :: Dynamic Content
Topic :: Internet :: WWW/HTTP :: WSGI
Topic :: Internet :: WWW/HTTP :: WSGI :: Application
Topic :: Office/Business :: Groupware
Topic :: Text Processing :: Markup""".splitlines(),

    # the tests and the jabber bot (it needs pyxmpp, which only exists
    # for Python 2) are not installed
    'packages': find_packages(include=['MoinMoin', 'MoinMoin.*'],
                              exclude=['*._tests', 'MoinMoin._tests']),

    'package_data': {'MoinMoin.i18n': ['README', 'Makefile', 'MoinMoin.pot', 'POTFILES.in',
                                       '*.po',
                                       'tools/*',
                                       'jabberbot/*',
                                      ],
                     'MoinMoin.web.static': make_filelist('MoinMoin/web/static/htdocs',
                                                          strip_prefix='MoinMoin/web/static/'),
                     'MoinMoin.support.flup': ['README.moin-py3'],
                    },

    'python_requires': '>=3.9',
    'install_requires': [
        'pygments',
        'passlib',
        'parsedatetime',
        # the cgi module was removed from the standard library in Python 3.13
        'legacy-cgi; python_version >= "3.13"',
    ],

    'entry_points': {
        'console_scripts': ['moin = MoinMoin.script.moin:run'],
    },

    # This copies the contents of wiki dir under sys.prefix/share/moin
    'data_files': makeDataFiles('share/moin', 'wiki'),
}


if __name__ == '__main__':
    setup(**setup_args)
