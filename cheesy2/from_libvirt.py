# libvirt python client packaging is a mess currently, so just calling
# virsh in a subprocess

import lxml.etree
import subprocess

def libvirt_list():
    p = subprocess.Popen(
        args=[
            'virsh',
            'list',
            '--all',
            ],
        stdout=subprocess.PIPE,
        close_fds=True,
        )

# $ virsh list --all
#  Id Name                 State
# ----------------------------------
#   9 autotest             running
#   - gold                 shut off
#   - kerntest             shut off
#   - kerntest2            shut off
#<blank>

    header = p.stdout.readline()
    assert header.split(None, 2) == ['Id', 'Name', 'State\n'], \
        "Unrecognized libvirt list header: %r" % header
    separator = p.stdout.readline()
    assert len(separator) > 5
    assert separator == len(separator[:-1]) * '-' + '\n', \
        "Unrecognized libvirt list separator: %r" % separator

    for line in p.stdout.xreadlines():
        if not line.endswith('\n'):
            raise RuntimeError('Got bad line from libvirt list failed: %r' % line)
        line = line[:-1]
        if not line:
            continue
        id_, name, state = line.split(None, 2)
        yield name

    if p.wait() != 0:
        raise RuntimeError('libvirt list failed, status %d' % p.returncode)

def get_libvirt_xml(name):
    p = subprocess.Popen(
        args=[
            'virsh',
            'dumpxml',
            '--domain={0}'.format(name),
            ],
        stdout=subprocess.PIPE,
        close_fds=True,
        )
    tree = lxml.etree.parse(p.stdout)
    if p.wait() != 0:
        raise RuntimeError('libvirt dumpxml failed, status %d' % p.returncode)
    return tree

def get_libvirt_xml_by_mac(macaddr):
    for domain in libvirt_list():
        tree = get_libvirt_xml(name=domain)
        for mac in tree.xpath("/domain/devices/interface[@type='network']/mac/@address"):
            if mac.replace(':', '-').lower() == macaddr:
                return tree

def get_libvirt_config(macaddr):
    tree = get_libvirt_xml_by_mac(macaddr)
    if tree is None:
        return {}
    r = {}
    # TODO not configurable at all -- does it need to be?

    for name in tree.xpath('/domain/name/text()'):
        r['local-hostname'] = '{0}.internal'.format(name)
        break

    return r

if __name__ == '__main__':
    import sys
    macaddr = sys.argv[1]
    tree = get_libvirt_config(macaddr)
    if tree is not None:
        tree = lxml.etree.tostring(tree)
        print tree
