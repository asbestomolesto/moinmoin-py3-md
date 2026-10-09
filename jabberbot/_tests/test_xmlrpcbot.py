# -*- coding: iso-8859-1 -*-
# MoinMoin 1.10.0 (Python 3 port): modified in 2026 by Claude (Anthropic AI)
# for Gabriele 'asbesto' Zaverio - see docs/CHANGES and the git history for details.
"""
    MoinMoin - XMLRPC bot tests

    @copyright: 2007 by Karol Nowak <grywacz@gmail.com>
    @license: GNU GPL, see COPYING for details.
"""

import pytest
from queue import Queue

try:
    import pyxmpp
except ImportError:
    pytest.skip("Skipping jabber bot tests - pyxmpp is not installed", allow_module_level=True)

import jabberbot.xmlrpcbot as xmlrpcbot
from jabberbot.config import BotConfig


class TestXMLRPCBotAPIs:
    def setup_class(self):
        self.queue_in = Queue()
        self.queue_out = Queue()
        self.bot = xmlrpcbot.XMLRPCClient(BotConfig, self.queue_in, self.queue_out)

    def testReportError(self):
        print("report_error() should put a command in the output queue")
        self.bot.report_error(["dude@example.com"], "Error %(err)s!", data={'err': 'bar!'})
        self.queue_out.get(False)

    def testWanrNoCredentials(self):
        print("warn_no_credentials() should put a command in the output queue")
        self.bot.warn_no_credentials(["dude@example.com"])
        self.queue_out.get(False)

