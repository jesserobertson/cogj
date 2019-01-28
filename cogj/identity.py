""" file:   identity.py (cogj)
    author: Jess Robertson, @jesserobertson
    date:   Sunday, 27 January 2019

    description: Mixin class to give classes autoincrementing IDs
"""

import itertools
from collections import defaultdict

class IdentityMixin:  # pylint: disable=R0903

    """
    Mixin class to add automatically incrementing IDs

    Adds an ident property which is automatically incremented
    as new instances are created
    """

    counters = defaultdict(itertools.count)

    @property
    def ident(self):
        "Return the identifier"
        try:
            return self._ident
        except AttributeError:
            self._ident = next(self.counters[self.__class__.__name__])
            return self._ident
