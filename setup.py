#!/usr/bin/env python3
""" file:   setup.py (cogj_tools)
    author: Jess Robertson
    date:   October 2016

    description: Setuptools installer script for cogj_tools.
"""

from setuptools import setup, find_packages

# Load requirements from requirements.txt etc
with open('requirements.txt', 'r') as src:
    REQUIREMENTS = src.readlines()
with open('requirements.dev.txt', 'r') as src:
    DEV_REQUIREMEBNTS = src.readlines()
with open('README.md', 'r') as src:
    README = src.read()

## PACKAGE INFORMATION
setup(
    name='cogj',
    version="0.0.1",
    description='Tooling for creating cloud-optimized GeoJSON files',
    long_description=README,
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
    install_requires=REQUIREMENTS,
    extras_require={
        'dev': DEV_REQUIREMEBNTS
    },
    tests_require=DEV_REQUIREMEBNTS,

    # Contents
    packages=find_packages(exclude=['test*']),
    include_package_data=True,
    test_suite="tests",

    # Some entry points for running rosedb
    entry_points={
        'console_scripts': [
            'cogj = cogj.cli:main',
        ],
    }
)
