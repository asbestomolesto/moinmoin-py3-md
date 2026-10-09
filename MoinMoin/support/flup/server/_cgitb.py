# Written by Claude (Anthropic AI) for Gabriele 'asbesto' Zaverio, 2026,
# as part of the Python 3 port of MoinMoin (version 1.10.0).
# The cgitb module was removed in Python 3.13, flup only uses its html()
# function to show tracebacks in debug mode.
import html as _html
import traceback


def html(exc_info):
    return '<pre>%s</pre>' % _html.escape(''.join(traceback.format_exception(*exc_info)))
