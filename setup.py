#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#from distutils.core import setup
from setuptools import setup

name_ = 'radiant grids'
version_ = '0.1'
packages_ = [
    'radiant',
    'radiant.grid',
    'radiant.grid.backend',
    'radiant.grid.adapter',
]

classifiers = [
    "Development Status :: 5 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: POSIX",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 3",
]

setup(
    name=name_,
    version=version_,
    author='Johan Egneblad',
    author_email='johan@DELETEMEegneblad.se',
    description='Grid environment',
    license="MIT",
    url='https://github.com/eblade/'+name_,
    download_url=('https://github.com/eblade/%s/archive/v%s.tar.gz'
                  % (name_, version_)),
    packages=packages_,
    scripts=['bin/grid', 'bin/gridserver'],
    classifiers = classifiers
)

