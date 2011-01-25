import sys
import os

def create():
    extra_args = [
        'auto',
        'locale=en_US',
        'console-setup/ask_detect=false',
        'console-setup/layoutcode=us',
        'netcfg/get_hostname=unassigned-hostname',
        'partman-lvm/confirm=true',
        'url=http://169.254.169.254/preseed/ubuntu-10.10',
        ]

    args = [
        'virt-install',
        '--connect=qemu:///system',
        '--noreboot',
        '--ram=256',
        '--arch=x86_64',
        '--os-type=linux',
        '--os-variant=ubuntumaverick',
        '--location=http://us.archive.ubuntu.com/ubuntu/dists/maverick/main/installer-amd64/',
        '--disk=pool=default,format=qcow2,size=4',
        '--extra-args={0}'.format(' '.join(extra_args)),
        ]
    args.extend(sys.argv[1:])
    os.execvpe(args[0], args, os.environ)
