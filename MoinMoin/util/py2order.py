# -*- coding: utf-8 -*-
"""
    MoinMoin - Python 2 dict ordering

    Some parsers dispatch a regex match to the handler of the first named
    group that matched, iterating over match.groupdict().items(). In
    Python 2 the order of that iteration was given by the dict hash order,
    and the parsers were developed and tested with that (fixed) order.
    Python 3 iterates in group definition order, which picks different
    handlers (e.g. "!WikiName" was rendered with the "!").

    This module emulates the CPython 2.7 dict (64 bit, no hash
    randomization), so match groups can be visited in the same order as
    MoinMoin 1.9 did on Python 2.

    @license: GNU GPL, see COPYING for details.
"""

MASK64 = (1 << 64) - 1

def py2_str_hash(s):
    """ hash() of an ascii str/unicode in CPython 2.7 (64 bit, no -R) """
    if not s:
        return 0
    b = s.encode('latin-1') if isinstance(s, str) else s
    x = (b[0] << 7) & MASK64
    for c in b:
        x = ((1000003 * x) ^ c) & MASK64
    x ^= len(b)
    if x >= 1 << 63:
        x -= 1 << 64
    if x == -1:
        x = -2
    return x

def py2_dict_order(keys):
    """ iteration order of a CPython 2.7 dict built by inserting keys in this order """
    size = 8
    table = [None] * size
    used = fill = 0
    def insert(table, key, h):
        mask = len(table) - 1
        i = h & mask
        if table[i] is None:
            table[i] = (key, h)
            return
        perturb = h & MASK64
        while True:
            i = (i << 2) + i + perturb + 1
            if table[i & mask] is None:
                table[i & mask] = (key, h)
                return
            perturb = perturb >> 5
    for key in keys:
        h = py2_str_hash(key)
        insert(table, key, h)
        used += 1
        fill += 1
        if fill * 3 >= len(table) * 2:
            minused = (2 if used > 50000 else 4) * used
            newsize = 8
            while newsize <= minused:
                newsize <<= 1
            old = table
            table = [None] * newsize
            for e in old:
                if e is not None:
                    insert(table, e[0], e[1])
            fill = used
    return [e[0] for e in table if e is not None]

_order_cache = {}


def py2_groupdict_order(pattern):
    """ order of match.groupdict().items() in Python 2 for a compiled pattern """
    try:
        return _order_cache[pattern]
    except KeyError:
        groupindex_order = py2_dict_order(list(pattern.groupindex))
        order = py2_dict_order(groupindex_order)
        _order_cache[pattern] = order
        return order


def groupdict_items(match):
    """ match.groupdict().items() in the order Python 2 used """
    groups = match.groupdict()
    return [(name, groups[name]) for name in py2_groupdict_order(match.re)]

