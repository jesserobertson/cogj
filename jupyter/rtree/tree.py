""" file:    tree.py (cogj)
    author:  Jess Robertson, jess@unearthed.solutions
    date:    Monday, 18 March 2019

    description: RTree implementation for writing data in cogj
"""

import math

from cogj.utilities import check_bounds
from .node import Node

class TreeBuilder:

    """
    Class to manage building an RTree from scratch
    """

    def __init__(self, min_items=4, max_items=10):
        # Configure order of RTree
        if min_items > max_items / 2:
            raise ValueError('min_items must be <= max_items / 2')
        else:
            self.max_items = max_items
            self.min_items = min_items

        # Set up internal storage
        self._nodes = None

    def __call__(self, nodes):
        """
        Construct a tree from the given node iterable

        Parameters:
            nodes - an iterable of `cogj.Node` instancs.
        """
        self._nodes = nodes

    def topology(self, n_items=None, as_dict=False):
        """
        Calcuate the topology of a fully packed RTree for bulk loading

        Parameters:
            n_items - the number of items to store. If None, uses the
                current count of items in the tree (i.e. the current height)
            as_dict - whether to return as a dict. Optional, defaults
                to False (return as tuple)
        """
        return {
            'height': self.height(n_items),
            'num_nodes': self.n_nodes(n_items),
            'num_subtrees': self.n_subtrees(n_items)
        } if as_dict else (
            self.height(n_items),
            self.n_nodes(n_items),
            self.n_subtrees(n_items)
        )

    def height(self, n_items=None):
        """
        Return the heigh of a tree required to store N items

        Parameters:
            n_items - the number of items to store. If None, uses the
                current count of items in the tree (i.e. the current height)
        """
        n_items = n_items or self.count
        return math.ceil(math.log(n_items, self.max_items)) \
            if n_items else 0

    def n_nodes(self, n_items=None):
        """
        Return the number of nodes required to store N items in the tree

        Parameters:
            n_items - the number of items to store. If None, uses the
                current count of items in the tree (i.e. the current number
                of nodes)
        """
        n_items = n_items or self.count
        return sum(
            math.ceil(n_items / float(self.min_items ** n))
            for n in range(1, self.height(n_items) + 1)
        ) if n_items else 0

    def n_subtrees(self, n_items=None):
        """
        Return the number of subtrees required at the root to generate a fully-packed
        RTree with the given number of nodes.

        Parameters:
            n_items - the number of items to store. If None, uses the
                current count of items in the tree (i.e. the current number
                of nodes)
        """
        n_items = n_items or self.count
        height = self.height(n_items)
        items_per_subtree = self.max_items ** (height - 1)
        return math.floor(math.sqrt(math.ceil(n_items / items_per_subtree)))

    def argsort(self, sort_direction, subset=None):
        """
        Do an argsort on (potentially a subset) of nodes in a particular
        direction (y or x)

        Parameters:
            sort_direction - the direction to sort in (0/'x' or 1/'y')
            subset - the subset of the nodes to sort
        """
        # Map direction to index
        try:
            sort_index = {'x': 0, 'y': 1}[sort_direction]
        except KeyError:
            sort_index = int(sort_direction)

        # Return soeted index
        return sorted(
            subset or range(len(self._nodes)),
            key=lambda i: self._nodes[i].centre[sort_index]
        )

    def pack(self, subset, sort_direction):
        """
        Pack nodes into the tree recursively

        Parameters:
            subset - the subset of nodes to pack into the tree
            sort_direction - the direction to sort in (0/'x' or 1/'y')
        """
        # If subset is small enough to pack into a leaf, do it
        if len(subset) <= self.max_items:
            return subset

        # Otherwise we need to keep splitting
        sort_idx = self.argsort(sort_direction=sort_direction, subset=subset)
        split = 


class Tree:

    """
    RTree class for managing geometries

    Parameters:
        min_items, max_items - the minimum and maximum entries in a
            node within the tree
    """

    def __init__(self):
        # Configure internal tree structure
        self._root = None
        self.depth = 0
        self.leaf_depth = 0
        self.count = 0

    def __len__(self):
        return self.count

    @property
    def root(self):
        "Return the root of the RTree"
        if self._root is None:
            self._root = Node()
            self.depth = 1
            self.leaf_depth = 1
        return self._root

    def construct(self, nodes):
        """
        Construct the RTree from the nodes.

        Uses a top-down balanced approach

        Parameters:
            nodes - a list of rtree.Node instances.
        """
        raise NotImplementedError()

    def search(self, bounds):
        "Find all rectangles that are stored in the tree which intersect these bounds"
        bounds = check_bounds(bounds)
        return self.root.search(bounds)

