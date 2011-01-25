===========================================================================
 Cheesy2 -- Provide Amazon EC2-style user data to libvirt virtual machines
===========================================================================

Cheesy2 is a small utility that does two things:

1. it provides EC2-style *meta-data* and *user-data* to libvirt
   virtual machines; the primary goal is to make ``cloud-init``
   in Ubuntu 10.10 work

2. it enabled automated installs via Debian/Ubuntu preseeding


Build
=====

First, build cheesy2::

	sudo apt-get install python-pip
	pip -E virtualenv install -r requirements.txt
	./virtualenv/bin/python setup.py develop

Then build the little C helper executable it needs::

	sudo apt-get install build-essential
	make mac-resolve


Setup
=====

To work, cheesy2 needs to respond to the IP address
``169.254.169.254``. Since every libvirt-using host will be doing that
internally, we don't want to actually set that up as a proper IP
address. Instead, let's NAT the traffic::

	sudo iptables -t nat -A PREROUTING --in-interface virbr+ -d 169.254.169.254 --proto tcp --dport 80 -j DNAT --to-destination 192.168.122.1:8076

(8076 as in 80=HTTP and 0x76=v=virtual)

This assumes your setup is the libvirt default, with
``192.168.122.0/24`` on ``virbr0``.

Note: this command needs to be re-run after reboots. Proper service
integration may follow later.


Run
===

Now we should be able to actually run cheesy2::

	./virtualenv/bin/paster serve paste.conf

Leave that running, and in another console, run::

	./virtualenv/bin/cheesy2-vm-create --name=test

That should run for a while (with Ubuntu 10.10, it downloads about
100MB and takes about 20 minutes, on my desktop machine).

Once it exits, your new virtual machine should be set up, and have
shut itself down. You can

- just start using it, manually configuring it as necessary;
  you may like using ``virt-manager``

- put files into ``metadata``, named after the internal hostname of
  the vm (typically the libvirt domain name + ``.internal``), to
  configure it:

  - ``foo.internal.json`` will set EC2-style metadata for vm ``foo``;
    see SSH example later

  - ``foo.internal.data`` will set EC2-style *user-data* for vm ``foo``;
    see resources later

- treat the vm as a *golden master*, never launch it but only clone
  it, using the clones as listed above


Authorizing SSH keys
====================

To automatically allow you to log in to a vm known as ``foo.internal``
as the default user ``ubuntu`` (who has passwordless sudo access), put
your SSH public key in ``metadata/foo.internal.json``::

	{
	  "public-keys": [
	    {"openssh-key": "ssh-rsa AAAA... me@mycomputer"}
	  ]
	}

Feel free to list multiple SSH public keys, by adding elements into
the JSON array.

Your changes take effect at the next boot of the vm, though some
things will only be configured once per instance (that is, if you
clone the vm, the clone will re-run the configuration).


Resources
=========

- Amazon EC2 documentation about metadata and user-data:

  http://docs.amazonwebservices.com/AWSEC2/latest/UserGuide/index.html?AESDG-chapter-instancedata.html

- Ubuntu help for ``cloud-init`` (user-data):

  https://help.ubuntu.com/community/CloudInit
