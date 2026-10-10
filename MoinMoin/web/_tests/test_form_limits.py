# -*- coding: utf-8 -*-
# Written by Claude (Anthropic AI) for Gabriele 'asbesto' Zaverio, 2026,
# as part of MoinMoin 1.11.0+md3 (security fixes).
"""
    MoinMoin - limits for the form data of a request (memory of the form
    fields, number of multipart parts: CVE-2023-25577 of the bundled Werkzeug)

    @license: GNU GPL, see COPYING for details.
"""

import pytest


class TestFormLimits(object):
    """ form data limits: number of multipart parts (CVE-2023-25577) and memory
        (MoinMoin 1.11.0+md3)
    """
    def parse(self, body, **limits):
        from io import BytesIO
        from MoinMoin.support.werkzeug.formparser import FormDataParser
        parser = FormDataParser(silent=False, **limits)
        return parser.parse(BytesIO(body), 'multipart/form-data', len(body), {'boundary': 'XX'})

    def body(self, parts, size=1):
        data = b''.join(b'--XX\r\nContent-Disposition: form-data; name="f%d"\r\n\r\n%s\r\n' % (i, b'x' * size)
                        for i in range(parts))
        return data + b'--XX--\r\n'

    def test_parts_limit(self):
        from MoinMoin.support.werkzeug.exceptions import RequestEntityTooLarge
        stream, form, files = self.parse(self.body(10), max_form_parts=10)
        assert len(form) == 10
        pytest.raises(RequestEntityTooLarge, self.parse, self.body(11), max_form_parts=10)

    def test_memory_limit(self):
        from MoinMoin.support.werkzeug.exceptions import RequestEntityTooLarge
        pytest.raises(RequestEntityTooLarge, self.parse, self.body(2, 1000), max_form_memory_size=1500)

    def test_moin_request_defaults(self):
        from MoinMoin.web.request import Request
        assert Request.max_form_parts == 1000
        assert Request.max_form_memory_size == 16 * 1024 * 1024
        from MoinMoin.config import multiconfig
        assert multiconfig.DefaultConfig.max_form_parts == 1000
        assert multiconfig.DefaultConfig.cookie_httponly is True
