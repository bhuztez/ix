#!/usr/bin/env python3

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name = 'ix',
    version = '0.0',

    url = 'https://github.com/bhuztez/ix',
    description = ' command line online judge client',
    license = 'BSD',

    classifiers = [
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3 :: Only",
    ],

    author = 'bhuztez',
    author_email = 'bhuztez@gmail.com',

    packages = ['ix', 'ix.clients', 'ix.credential', 'ix.credential.readers', 'ix.credential.storages'],
    install_requires= ['lxml'],
    zip_safe = False,
)
