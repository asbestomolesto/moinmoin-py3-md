# -*- coding: utf-8 -*-
# Written by Claude (Anthropic AI) for Gabriele 'asbesto' Zaverio, 2026
# (moinmoin-py3-md 1.12.1).
"""
    MoinMoin - MoinMoin.util.timefuncs Tests

    @license: GNU GPL, see COPYING for details.
"""

import time

from MoinMoin.util import timefuncs


def test_tmtuple_now():
    # tmtuple() without argument is "now" (the Preferences page crashed on it)
    now = time.time()
    t = timefuncs.tmtuple()
    assert abs(time.mktime(t) - time.mktime(time.gmtime(now))) < 5


def test_tmtuple_near_zero_means_now():
    # values around 0 are taken as "not set" (original MoinMoin behaviour)
    t = timefuncs.tmtuple(3600)
    assert abs(time.mktime(t) - time.mktime(time.gmtime())) < 5


def test_tmtuple_given_time():
    assert timefuncs.tmtuple(10 ** 9)[:6] == time.gmtime(10 ** 9)[:6]
