import restish.app
import restish.page

from restish import resource
from restish import http

from cheesy2 import arp

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

    @resource.child('')
    def index(self, request, segments):
        def g():
            for k,v in sorted(self.metadata.iteritems()):
                if isinstance(v, dict):
                    yield '{0}/\n'.format(k)
                else:
                    yield '{0}\n'.format(k)

        return http.ok(
            [('Content-Type', 'text/plain')],
            g(),
            )

    @resource.child(resource.any)
    def child(self, request, segments):
        meta = self.metadata.get(segments[0])
        if meta is None:
            return http.not_found()
        elif isinstance(meta, dict):
            return MetaData(metadata=meta), segments[1:]
        else:
            return http.ok(
                [('Content-Type', 'text/plain')],
                [meta],
                )

def get_metadata(metadata_dir, request):
    ipaddr = request.remote_addr
    try:
        macaddr = arp.get_mac_address(ipaddr)
    except arp.ArpResolutionError as e:
        return {}
    return {
        'cheesy2-ip-address-seen': ipaddr,
        'cheesy2-mac-address-seen': macaddr,
        # not sure if this is the smartest thing, but it is unique
        'instance-id': macaddr,
        'local-hostname': 'vm{0}.internal'.format(macaddr)
        }

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
