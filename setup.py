#!/usr/bin/env python3
""" file:   setup.py (cogj_tools)
    author: Jess Robertson
    date:   October 2016

    description: Setuptools installer script for cogj_tools.
"""

import os
from setuptools import setup, find_packages

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
    packages=find_packages(exclude=['test*']),
    include_package_data=True,
    test_suite="tests",

    # Some entry points for running rosedb
    entry_points={
        'console_scripts': [
            'cogj = cogj.cli:cogj',
        ],
    }
)
