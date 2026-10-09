# MoinMoin 1.10.0 (Python 3 port): modified in 2026 by Claude (Anthropic AI)
# for Gabriele 'asbesto' Zaverio - see docs/CHANGES and the git history for details.
# taken from Amos' XML-RPC HowTo:

import xmlrpc.client as xmlrpclib, http.client
from base64 import b64encode

class BasicAuthTransport(xmlrpclib.Transport):
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
        self.verbose = 0

    def request(self, host, handler, request_body, **kw):
        # issue XML-RPC request
        h = http.client.HTTP(host)
        h.putrequest("POST", handler)

        # required by HTTP/1.1
        h.putheader("Host", host)

        # required by XML-RPC
        h.putheader("User-Agent", self.user_agent)
        h.putheader("Content-Type", "text/xml")
        h.putheader("Content-Length", str(len(request_body)))

        # basic auth
        if self.username is not None and self.password is not None:
            authhdr = "Basic %s" % b64encode(("%s:%s" % (self.username, self.password)).encode('utf-8')).decode('ascii')
            h.putheader("Authorization", authhdr)
        h.endheaders()

        if request_body:
            h.send(request_body)

        errcode, errmsg, headers = h.getreply()

        if errcode != 200:
            raise xmlrpclib.ProtocolError(
                host + handler,
                errcode, errmsg,
                headers
                )

        return self.parse_response(h.getfile())

