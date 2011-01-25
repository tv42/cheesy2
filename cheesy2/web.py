import errno
import json
import os
import restish.app
import restish.page

from restish import resource
from restish import http

from cheesy2 import arp
from cheesy2 import from_libvirt

class Named(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return '{class_}(name={name!r}, value={value!r})'.format(
            class_=self.__class__.__name__,
            name=self.name,
            value=self.value,
            )

class Cheesy2(resource.Resource):

    @resource.child()
    def latest(self, request, segments):
        return APIVersion()

    @resource.child('2009-04-04')
    def api_2009_04_04(self, request, segments):
        return APIVersion()

class APIVersion(resource.Resource):

    @resource.child('meta-data')
    def meta_data(self, request, segments):
        meta = request.environ['cheesy2.metadata'](request)
        return MetaData(metadata=meta)

class MetaData(resource.Resource):

    def __init__(self, metadata):
        super(MetaData, self).__init__()
        self.metadata = metadata

    @resource.GET()
    def serve(self, request):
        if isinstance(self.metadata, (dict, list)):
            return http.not_found()
        else:
            return http.ok(
                [('Content-Type', 'text/plain')],
                [self.metadata],
                )

    @resource.child('')
    def index(self, request, segments):
        def g():
            if isinstance(self.metadata, dict):
                for k,v in sorted(self.metadata.iteritems()):
                    if isinstance(v, dict):
                        yield '{0}/\n'.format(k)
                    elif isinstance(v, list):
                        yield '{0}/\n'.format(k)
                    else:
                        yield '{0}\n'.format(k)
            elif isinstance(self.metadata, list):
                for i, v in enumerate(self.metadata):
                    name = ''
                    if isinstance(v, Named):
                        name = v.name
                    yield '{0}={1}\n'.format(i, name)
            else:
                raise RuntimeError('Cannot index weird metadata: %r' % self.metadata)

        return http.ok(
            [('Content-Type', 'text/plain')],
            g(),
            )

    @resource.child(resource.any)
    def child(self, request, segments):
        if isinstance(self.metadata, dict):
            meta = self.metadata.get(segments[0])
        elif isinstance(self.metadata, list):
            try:
                index = int(segments[0])
            except ValueError:
                meta = None
            else:
                if index < 0:
                    meta = None
                else:
                    try:
                        meta = self.metadata[index]
                    except IndexError:
                        meta = None
        else:
            meta = None

        if meta is None:
            return http.not_found()

        if isinstance(meta, Named):
            meta = meta.value

        return MetaData(metadata=meta), segments[1:]

def get_metadata(metadata_dir, request):
    ipaddr = request.remote_addr
    try:
        macaddr = arp.get_mac_address(ipaddr)
    except arp.ArpResolutionError as e:
        return {}
    meta = {
        'cheesy2-ip-address-seen': ipaddr,
        'cheesy2-mac-address-seen': macaddr,
        # not sure if this is the smartest thing, but it is unique
        'instance-id': macaddr,
        'local-hostname': 'vm{0}.internal'.format(macaddr)
        }
    virt = from_libvirt.get_libvirt_config(macaddr)
    meta.update(virt)
    try:
        with file(os.path.join(metadata_dir, '{0}.json'.format(macaddr))) as f:
            custom = json.load(f)
    except IOError, e:
        if e.errno == errno.ENOENT:
            pass
        else:
            raise
    else:
        meta.update(custom)
    return meta

def setup_environ(app, global_config, local_config):
        """
        WSGI application wrapper factory for extending the WSGI environ with
        application-specific keys.
        """
        metadata_dir = local_config.get('metadata-dir', 'metadata')
        def _get_metadata(request):
            return get_metadata(metadata_dir, request)

        def application(environ, start_response):
            # use setdefault so unittests can override this
            environ.setdefault('cheesy2.metadata', _get_metadata)

            return app(environ, start_response)

        return application

def app_factory(global_config, **local_config):
    root = Cheesy2()
    app = restish.app.RestishApp(root)
    app = setup_environ(app, global_config, local_config)
    return app
