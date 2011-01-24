from nose.tools import eq_ as eq
import webtest

from cheesy2 import web

def test_metadata_index():
    app = web.app_factory(global_config={})
    app = webtest.TestApp(app)
    res = app.get(
        '/latest/meta-data/',
        extra_environ={
            'cheesy2.metadata': lambda request: {
                'foo': 'bar',
                'baz': 'quux',
                },
            },
        )
    eq(res.headers['Content-Type'], 'text/plain')
    eq(res.body, 'baz\nfoo\n')

def test_metadata_specific():
    app = web.app_factory(global_config={})
    app = webtest.TestApp(app)
    res = app.get(
        '/latest/meta-data/hostname',
        extra_environ={
            'cheesy2.metadata': lambda request: {
                'hostname': 'slartibartfast.example.com',
                },
            },
        )
    eq(res.headers['Content-Type'], 'text/plain')
    eq(res.body, 'slartibartfast.example.com')

def test_metadata_specific_notfound():
    app = web.app_factory(global_config={})
    app = webtest.TestApp(app)
    res = app.get(
        '/latest/meta-data/does-not-exist',
        extra_environ={
            'cheesy2.metadata': lambda request: {
                'hostname': 'slartibartfast.example.com',
                },
            },
        status=404,
        )
    eq(res.headers['Content-Type'], 'text/plain')
    eq(res.body, '404 Not Found')

def test_metadata_dict():
    app = web.app_factory(global_config={})
    app = webtest.TestApp(app)
    res = app.get(
        '/latest/meta-data/',
        extra_environ={
            'cheesy2.metadata': lambda request: {
                'foo': 'bar',
                'baz': {
                    'one': 'a',
                    'two': 'b',
                    },
                },
            },
        )
    eq(res.headers['Content-Type'], 'text/plain')
    eq(res.body, 'baz/\nfoo\n')