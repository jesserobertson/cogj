""" file:    test_utilities.py (tests)
    author: Jess Robertson, jess@unearthed.solutions
    date:    Sunday, 10 February 2019

    description: Tests for utilities
"""

import unittest

import ddt

from cogj.utilities import flatten

@ddt.ddt
class TestFlatten(unittest.TestCase):

    "Test flatten routine"

    @ddt.data(
        [[2, 3], [4], [5, 6, 7]],
        [(2, 3), (4,), (5, 6, 7)],
        ([2, 3], (4,), [5, 6, 7])
    )
    def test_flatten(self, data):
        "Check things flatten ok"
        output = list(flatten(data))
        self.assertEqual(len(output), 6)
        self.assertTrue(isinstance(output, list))
        self.assertEqual(output, [2, 3, 4, 5, 6, 7])


if __name__ == '__main__':
    unittest.main()