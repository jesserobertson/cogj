""" file:    utilities.py (cogj)
    author: Jess Robertson, @jesserobertson
    date:    Sunday, 27 January 2019

    description: Iteration utilities etc for cogj
"""

import collections
import itertools

from toolz import curry

@curry
def grouper(size, iterable):
    "Group an iterable in chunks of `size`"
    iterator = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(iterator, size))
        if not chunk:
            return None
        yield chunk

def flatten(list_of_lists):
    "Flatten a list of list of ... of lists"
    for elem in list_of_lists:
        if isinstance(elem, collections.Iterable) and not isinstance(elem, (str, bytes)):
            yield from flatten(elem)
        else:
            yield elem
