import subprocess

class ArpResolutionError(Exception):
    """ARP resolution error"""

    def __str__(self):
        return '{doc}: {message}'.format(
            doc=self.__doc__,
            message=': '.join(self.args),
            )

def get_mac_address(ipaddr, iface='virbr0'):
    p = subprocess.Popen(
        args=[
            './mac-resolve',
            iface,
            ipaddr,
            ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        close_fds=True,
        )
    (stdout, stderr) = p.communicate()
    if stderr:
        raise ArpResolutionError('{stderr} (exit status {code})'.format(
                stderr=stderr.rstrip('\n'),
                code=p.returncode,
                ))
    if p.returncode != 0:
        raise ArpResolutionError('ARP resolve failed without message (exit status {code})'.format(
                code=p.returncode,
                ))
    lines = stdout.splitlines()
    assert len(lines) == 1
    (mac,) = lines
    return mac

if __name__ == '__main__':
    import sys
    print get_mac_address(iface=sys.argv[1], ipaddr=sys.argv[2])
