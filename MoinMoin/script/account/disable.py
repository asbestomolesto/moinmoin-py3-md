# -*- coding: iso-8859-1 -*-
# MoinMoin 1.10.0 (Python 3 port): converted to Python 3 (2to3) in 2026 by
# Claude (Anthropic AI) for Gabriele 'asbesto' Zaverio.
# Modified by Claude (Anthropic AI) (moinmoin-py3-md 1.12.1): the account keeps
# its name, email and subscriptions, "account enable" undoes it.
"""
MoinMoin - disable a user account

@copyright: 2006 MoinMoin:ThomasWaldmann
@license: GNU GPL, see COPYING for details.
"""

from MoinMoin.script import MoinScript

class PluginScript(MoinScript):
    """\
Purpose:
========
This tool allows you to disable user accounts via a command line interface.
A disabled account cannot log in any more. Its name, email, password and
subscriptions are kept, so "moin ... account enable" can enable it again.
To delete an account for good, use "moin ... account delete".

Detailed Instructions:
======================
General syntax: moin [options] account disable [disable-options]

[options] usually should be:
    --config-dir=/path/to/my/cfg/ --wiki-url=http://wiki.example.org/

[disable-options] see below:
    1. To disable the user 'JohnSmith':
       moin ... account disable --name JohnSmith

    2. To disable the user 'JohnSmith', based on his UID '1198872910.78.56322':
       moin ... account disable --uid 1198872910.78.56322
"""

    def __init__(self, argv, def_values):
        MoinScript.__init__(self, argv, def_values)
        self.parser.add_option(
            "--uid", metavar="UID", dest="uid",
            help="Disable the user with user id UID."
        )
        self.parser.add_option(
            "--name", metavar="NAME", dest="uname",
            help="Disable the user with user name NAME."
        )

    def mainloop(self):
        # we don't expect non-option arguments
        if len(self.args) != 0:
            self.parser.error("incorrect number of arguments")

        flags_given = self.options.uid or self.options.uname
        if not flags_given:
            self.parser.print_help()
            import sys
            sys.exit(1)

        self.init_request()
        request = self.request

        from MoinMoin import user
        if self.options.uid:
            u = user.User(request, self.options.uid)
        elif self.options.uname:
            u = user.User(request, user.getUserIdIncludingDisabled(request, self.options.uname))

        if not u.exists():
            print('This user "%s" does not exists!' % (self.options.uname or self.options.uid))
            return

        print(" %-20s %-25s %-35s" % (u.id, u.name, u.email), end=' ')
        if u.disable():
            print("- disabled.")
        else:
            print("- is already disabled.")
