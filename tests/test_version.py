""" file:    test_version.py (tests)
    author:  Jess Robertson
    date:    Tuesday, 15 January 2019

    description: Tests for version
"""

import unittest

import cogj

class TestVersion(unittest.TestCase):

    "Check version is set"

    def test_version(self):
        "Check version is set"
        self.assertTrue(cogj.__version__ is not None)

if __name__ == '__main__':
    unittest.main()