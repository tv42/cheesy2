#!/usr/bin/python
from setuptools import setup, find_packages, Extension

setup(
    name='cheesy2',
    version='0.0.1',
    packages=find_packages(),

    author='Tommi Virtanen',
    author_email='tommi.virtanen@dreamhost.com',
    description='Provide Amazon EC2-style user data to libvirt virtual machines',
    license='MIT',
    keywords='libvirt virtualization',

    install_requires=[
        'restish >=0.11',
        ],

    # ext_modules=[
    #     Extension(
    #         'arp',
    #         ['arp.c'],
    #         extra_compile_args=['-Werror'],
    #         ),
    #     ],

    entry_points={
        'paste.app_factory': [
            'main=cheesy2.web:app_factory',
            ],
        },
    )
