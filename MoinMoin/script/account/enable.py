# -*- coding: iso-8859-1 -*-
# Written by Claude (Anthropic AI) for Gabriele 'asbesto' Zaverio, 2026
# (moinmoin-py3-md 1.12.1), modelled on account/disable.py.
"""
MoinMoin - enable a disabled user account

@license: GNU GPL, see COPYING for details.
"""

from MoinMoin.script import MoinScript

class PluginScript(MoinScript):
    """\
Purpose:
========
This tool allows you to enable again a user account that was disabled with
"moin ... account disable" or with the account browser of the SystemAdmin
page. Accounts disabled by moin 1.12.0 or older were renamed to
"<name>-<user id>": they get their original name and email back.

Detailed Instructions:
======================
General syntax: moin [options] account enable [enable-options]

[options] usually should be:
    --config-dir=/path/to/my/cfg/ --wiki-url=http://wiki.example.org/

[enable-options] see below:
    1. To enable the user 'JohnSmith':
       moin ... account enable --name JohnSmith

    2. To enable the user 'JohnSmith', based on their UID '1198872910.78.56322':
       moin ... account enable --uid 1198872910.78.56322
"""

    def __init__(self, argv, def_values):
        MoinScript.__init__(self, argv, def_values)
        self.parser.add_option(
            "--uid", metavar="UID", dest="uid",
            help="Enable the user with user id UID."
        )
        self.parser.add_option(
            "--name", metavar="NAME", dest="uname",
            help="Enable the user with user name NAME."
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
        else:
            u = user.User(request, user.getUserIdIncludingDisabled(request, self.options.uname, renamed=True))

        if not u.exists():
            print('This user "%s" does not exists!' % (self.options.uname or self.options.uid))
            return

        print(" %-20s %-25s %-35s" % (u.id, u.name, u.email), end=' ')
        if u.enable():
            print("- enabled (now: %s %s)." % (u.name, u.email))
        else:
            print("- is not disabled.")
