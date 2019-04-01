""" file:    node.py (rtree)
    author: Jess Robertson, jess@unearthed.solutions
    date:    Monday, 18 March 2019

    description: Node implementation for rtree
"""

from math import inf
from collections import namedtuple

from cogj.identity import IdentityMixin
from cogj.utilities import check_bounds, flatten

Point = namedtuple('Point', ['x', 'y'])

class Node(IdentityMixin):

    """
    On the first day of Christmas, my true love gave to me...
    ...a no-o-ode in an RTree 🎵

    Parameters:
        bounds - the bounding box for the node
        level - the level of the node in the tree. Optional, defaults
            to None
        children - the children of the node. Optional, defaults to the
            empty list.
        parent - the parent of the node. Optional, defaults to None.
    """

    def __init__(self, bounds=None, level=None, children=None, parent=None):
        self.bounds = check_bounds(bounds or (-inf, -inf, inf, inf))
        self._centre = None
        self.children = children or []
        self.parent = parent
        self.level = level or 0
        self.is_leaf = True

    def intersects(self, other):
        "Check whether this node intersects with another node"
        bb1 = self.bounds
        try:
            bb2 = other.bounds
        except AttributeError:
            bb2 = other
        return (
            (bb2[0] > bb1[2]) or
            (bb2[2] < bb1[0]) or
            (bb2[3] > bb1[1]) or
            (bb2[1] < bb1[3])
        )

    @property
    def centre(self):
        "Return the centroid of the bounds"
        if self._centre is None:
            self._centre = Point(
                (self.bounds[0] + self.bounds[2]) / 2,
                (self.bounds[1] + self.bounds[3]) / 2
            )
        return self._centre

    def search(self, bounds):
        "Range search helper. Does no checking of bounds validity"
        intersections = [c for c in self.children if c.intersects(bounds)]
        return intersections if self.is_leaf else \
            flatten([c.search(bounds) for c in intersections])
