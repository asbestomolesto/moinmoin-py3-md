# -*- coding: iso-8859-1 -*-
"""
MoinMoin Testing Framework
--------------------------

All test modules must be named test_modulename to be included in the
test suite. If you are testing a package, name the test module
test_package_module.

Tests that need the current request, for example to create a page
instance, can refer to self.request. It is injected into all test case
classes by the framework.

Tests that require a certain configuration, like section_numbers = 1, must
use a Config class to define the required configuration within the test class.

@copyright: 2005 MoinMoin:NirSoffer,
            2007 MoinMoin:AlexanderSchremmer,
            2008 MoinMoin:ThomasWaldmann
@license: GNU GPL, see COPYING for details.
"""

import inspect
import os
import sys

import pytest

moindir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, moindir)

from MoinMoin.web.request import TestRequest, Client
from MoinMoin.wsgiapp import Application, init
from MoinMoin._tests import maketestwiki, wikiconfig


def init_test_request(given_config=None, static_state=[False]):
    if not static_state[0]:
        maketestwiki.run(True)
        static_state[0] = True
    request = TestRequest()
    request.given_config = given_config
    request = init(request)
    return request


# pytest customization starts here
#
# The original suite was written for py.test 1.x: every test module gets a
# MoinMoin request built from the test wiki configuration, test classes get
# self.request and self.client (built from cls.Config when present), and a
# test function asking for an argument called "request" receives the
# MoinMoin request instead of the pytest fixture request.

def _module_request(module):
    if '_moin_request' not in module.__dict__:
        module._moin_request = init_test_request(given_config=wikiconfig.Config)
    return module._moin_request


def _prepare_class(cls, module):
    if '_moin_prepared' in cls.__dict__:
        return
    if hasattr(cls, 'Config'):
        cls.request = init_test_request(given_config=cls.Config)
        cls.client = Client(Application(cls.Config))
    else:
        request = _module_request(module)
        cls.request = request
        cls.client = Client(Application(request.cfg.__class__))
    cls._moin_prepared = True


def _moin_request_for(item):
    if item.cls is not None:
        return item.cls.request
    return _module_request(item.module)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    module = getattr(item, 'module', None)
    if module is None:
        return
    _module_request(module)
    if item.cls is not None:
        _prepare_class(item.cls, module)


def _call(func, request):
    try:
        params = inspect.signature(func).parameters
    except (TypeError, ValueError):
        params = {}
    if 'request' in params:
        return func(request)
    return func()


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    request = _moin_request_for(pyfuncitem)
    if isinstance(pyfuncitem, YieldTestItem):
        _run_generator(pyfuncitem.obj, request)
        return True
    argnames = pyfuncitem._fixtureinfo.argnames
    if 'request' not in argnames:
        return None
    kwargs = dict((name, pyfuncitem.funcargs[name]) for name in argnames)
    kwargs['request'] = request
    pyfuncitem.obj(**kwargs)
    return True


def _run_generator(func, request):
    if 'request' in inspect.signature(func).parameters:
        gen = func(request)
    else:
        gen = func()
    for case in gen:
        if callable(case):
            case = (case, )
        if isinstance(case[0], str):
            # py.test 1.x also allowed yielding (name, check, args...)
            case = case[1:]
        check, args = case[0], case[1:]
        check(*args)


class YieldTestItem(pytest.Function):
    """ a generator test ("yield test" of py.test 1.x): all generated checks
        run inside one test item """


@pytest.hookimpl(tryfirst=True)
def pytest_pycollect_makeitem(collector, name, obj):
    if (inspect.isgeneratorfunction(obj) and collector.funcnamefilter(name)):
        return YieldTestItem.from_parent(collector, name=name)
    return None
