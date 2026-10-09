#!/usr/bin/env python
# MoinMoin 1.10.0 (Python 3 port): modified in 2026 by Claude (Anthropic AI)
# for Gabriele 'asbesto' Zaverio - see docs/CHANGES and the git history for details.
"""
This script is a sample for xmlrpc calls.

It calls the HelloWorld.py xmlrpc plugin.

GPL software, 2003-08-10 Thomas Waldmann
"""

def run():
    import xmlrpc.client as xmlrpclib
    srcwiki = xmlrpclib.ServerProxy("http://master.moinmo.in/?action=xmlrpc2")
    print(srcwiki.HelloWorld("Hello Wiki User!\n"))

if __name__ == "__main__":
    run()

