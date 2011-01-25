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

def test_metadata_list():
    app = web.app_factory(global_config={})
    app = webtest.TestApp(app)
    meta = {
        'cheesy2.metadata': lambda request: {
            'foo': 'bar',
            'public-keys': [
                web.Named(name='my-public-key', value={'openssh-key': 'ssh-rsa AAAAfoo my-public-key'}),
                ],
            },
        }

    res = app.get(
        '/latest/meta-data/',
        extra_environ=meta,
        )
    eq(res.headers['Content-Type'], 'text/plain')
    eq(res.body, 'foo\npublic-keys/\n')

    res = app.get(
        '/latest/meta-data/public-keys/',
        extra_environ=meta,
        )
    eq(res.headers['Content-Type'], 'text/plain')
    eq(res.body, '0=my-public-key\n')

    res = app.get(
        '/latest/meta-data/public-keys/0/',
        extra_environ=meta,
        )
    eq(res.headers['Content-Type'], 'text/plain')
    eq(res.body, 'openssh-key\n')

    res = app.get(
        '/latest/meta-data/public-keys/0/openssh-key',
        extra_environ=meta,
        )
    eq(res.headers['Content-Type'], 'text/plain')
    eq(res.body, 'ssh-rsa AAAAfoo my-public-key')
