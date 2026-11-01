# -*- coding: iso-8859-1 -*-
# Written by Claude (Anthropic AI) for Gabriele 'asbesto' Zaverio, 2026
# (moinmoin-py3-md 1.12.1), modelled on account/disable.py.
"""
MoinMoin - delete a user account for good

@license: GNU GPL, see COPYING for details.
"""

from MoinMoin.script import MoinScript

class PluginScript(MoinScript):
    """\
Purpose:
========
This tool allows you to delete a user account for good: its profile file
in data/user/ is removed, so the name and the email can be used by a new
account. This cannot be undone (keep a backup of data/user/ if unsure).
The pages and the edits made by the user stay in the wiki; the page
history shows the user id instead of the name.

To lock an account out only for a while, use "moin ... account disable".

Detailed Instructions:
======================
General syntax: moin [options] account delete [delete-options]

[options] usually should be:
    --config-dir=/path/to/my/cfg/ --wiki-url=http://wiki.example.org/

[delete-options] see below:
    1. To delete the user 'JohnSmith':
       moin ... account delete --name JohnSmith

    2. To delete the user 'JohnSmith', based on their UID '1198872910.78.56322':
       moin ... account delete --uid 1198872910.78.56322
"""

    def __init__(self, argv, def_values):
        MoinScript.__init__(self, argv, def_values)
        self.parser.add_option(
            "--uid", metavar="UID", dest="uid",
            help="Delete the user with user id UID."
        )
        self.parser.add_option(
            "--name", metavar="NAME", dest="uname",
            help="Delete the user with user name NAME."
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
        u.delete()
        print("- deleted.")
