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

def check_bounds(bounds):
    """
    Check a bounds array is correct, raise ValueError if not

    Parameters:
        bounds - the bounds array to check. Of form (minx, miny, maxx, maxy)
            or (left, bottom, right, top).

    Returns:
        the bounds array, if valid
    """
    if not ((bounds[0] <= bounds[2]) and (bounds[1] <= bounds[3])):
        raise ValueError('Bounds should be (minx, miny, maxx, maxy)')
    return bounds

def argsort(iterable, subset=None):
    """
    Perform an argsort (return the indices which generate a sort) in base
    Python (doesn't require numpy).

    Note that your iterable must support random access through
    __getitem__, otherwise we can't look up items to sort them!

    Parameters:
        iterable - the iterable to sort. Must implement __getiem__.
        subset - a list of indices to sort. Useful if you only want
            to sort a subset of the array without pulling out these
            indices
    """
    if subset is not None:
        index = subset
    else:
        # Sort the entire thing
        index = range(len(iterable))
    return sorted(index, key=iterable.__getitem__)
