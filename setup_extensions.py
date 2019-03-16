""" file:    setup_extensions.py (cogj)
    author:  Jess Robertson, @jesserobertson
    date:    Saturday, 16 March 2019

    description: Set up Cython extensions for CO-GJ
"""

from pathlib import Path
from logging import getLogger
from multiprocessing import cpu_count

import numpy
from setuptools import Extension
from setuptools.command.sdist import sdist

# Here we try to import Cython - if it's here then we can generate new c sources
# directly from the pyx files using their build_ext class.
# If not then we just use the default setuptools version
try:
    from Cython.Distutils import build_ext
    HAVE_CYTHON = True
except ImportError:
    from setuptools.command.build_ext import build_ext
    HAVE_CYTHON = False

LOGGER = getLogger()

# Where are our extensions located?
EXTENSIONS_MODULE = Path('cogj/extensions')

def update_thread_count():
    """ Update the thread count for OpenMP extensions

        Uses one thread per core, with the estimate of the number of cores from
        multiprocessing.cpu_count.
    """
    LOGGER.info('Updating thread count for cython code to %s', cpu_count())
    num_threads = cpu_count()  # We're just going for 1 thread/CPU here
    fname = EXTENSIONS_MODULE / 'common.pxd'

    # Don't clobber other definitions
    try:
        with open(fname, 'r') as src:
            content = src.readlines()  # this is short, just slurp it

        # Write out a new definition
        with open(fname, 'w') as sink:
            for line in content:
                if line.startswith('cdef int NUM_THREADS'):
                    sink.write('cdef int NUM_THREADS = {0}'.format(num_threads))
                else:
                    sink.write(line)

    except FileNotFoundError:
        # doesn't exist so just leave it
        with open(fname, 'w') as sink:
            sink.write('cdef int NUM_THREADS = {0}'.format(num_threads))



def get_extensions():
    """ Find our extensions to build.

        Also updates the thread count for OpenMP extensions to the number of CPUs
        availble on the current machine.

        Returns:
            a list of Extension objects to pass to setup
    """
    update_thread_count()

    # Get the extensions
    if HAVE_CYTHON:
        files = [f for f in EXTENSIONS_MODULE.iterdir() if f.suffix == '.pyx']
    else:
        files = [f for f in EXTENSIONS_MODULE.iterdir() if f.suffix == '.c']

    # Construct keyword arguments for all extensions
    kwargs = dict(
        # extra_compile_args=['-fopenmp'],
        # extra_link_args=['-fopenmp'],
        include_dirs=[numpy.get_include(), EXTENSIONS_MODULE]
    )

    # Construct all the extension objects and return them
    extensions = []
    for fname in files:
        module_name = fname.stem
        extension_name = '.'.join(list(EXTENSIONS_MODULE.parts) + [module_name])
        source = str(fname)
        extensions.append(Extension(extension_name, sources=[source], **kwargs))
    return extensions

# Update source distribution - we always require Cython for this...
class cython_sdist(sdist):

    def run(self):
        # Make sure the compiled Cython files in the distribution are up-to-date
        from Cython.Build import cythonize
        update_thread_count()
        cythonize([str(f)
                   for f in EXTENSIONS_MODULE.iterdir()
                   if f.suffix == '.pyx'])
        super().run()

def get_cmdclass():
    """ Return a command class which builds cython extensions automatically
    """
    cmdclass = {
        'build_ext': build_ext,
        'sdist': cython_sdist
    }
    return cmdclass
