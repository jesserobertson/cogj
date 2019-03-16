#!/usr/bin/env python3
""" file:   setup.py (cogj)
    author: Jess Robertson, @jesserobertson
    date:   October 2016

    description: Setuptools installer script for cogj.
"""

import textwrap
import sys
import os

# Check that our version of setuptools is new enough
# Resolving Cython and numpy dependencies via 'setup_requires' requires setuptools >= 18.0:
# https://github.com/pypa/setuptools/commit/a811c089a4362c0dc6c4a84b708953dde9ebdbf8
import pkg_resources
try:
    pkg_resources.require('setuptools >= 18.0')
except pkg_resources.ResolutionError:
    print(textwrap.dedent("""
          setuptools >= 18.0 is required, and the dependency cannot be
          automatically resolved with the version of setuptools that is
          currently installed (%s).

          You can upgrade setuptools:
          $ pip install -U setuptools
          """ % pkg_resources.get_distribution("setuptools").version),
          file=sys.stderr)
    sys.exit(1)

# Now we can do all our imports
from setuptools import setup, find_packages
from setup_extensions import get_extensions, get_cmdclass

# Get extensions and update comandclass
EXTENSIONS = get_extensions()
CMDCLASS = get_cmdclass()

def read(*paths, lines=False):
    """
    Build a file path from *paths and return the contents.

    Parameters:
        lines - if True, return a list of lines. Defaults to
            False (send back raw text).
    """
    with open(os.path.join(*paths), 'r') as src:
        return src.readlines() if lines else src.read()

## PACKAGE INFORMATION
setup(
    name='cogj',
    version="0.0.1",
    description='Tooling for creating cloud-optimized GeoJSON files',
    long_description=read('README.md'),
    author='Jess Robertson',
    author_email='jessrobertson@icloud.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Operating System :: POSIX : Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet',
        'Topic :: Geospatial',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    # Dependencies
    install_requires=read('requirements.txt', lines=True),
    extras_require={
        'dev': read('requirements.dev.txt', lines=True)
    },
    tests_require=read('requirements.dev.txt', lines=True),

    # Contents
    packages=find_packages(exclude=['test*', 'flask']),
    include_package_data=True,
    test_suite="tests",

    # Cython extensions & other stuff
    cmdclass=CMDCLASS,
    ext_modules=EXTENSIONS,

    # Some entry points for running rosedb
    entry_points={
        'console_scripts': [
            'cogj = cogj.cli:cogj',
        ],
    }
)
