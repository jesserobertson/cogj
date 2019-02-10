""" file:    test_reproject.py (tests)
    author: Jess Robertson, jess@unearthed.solutions
    date:    Sunday, 10 February 2019

    description: Simple tests for reprojection
"""

import unittest

import ddt
from shapely import geometry

from cogj.reproject import reproject
from cogj import FeatureCollection, Feature

GEOMS = (
    geometry.Point(0, 0),
    geometry.MultiPoint([[0, 0], [1, 1]]),
    geometry.LineString([[0, 0], [1, 1]]),
    geometry.Polygon([[0, 0], [1, 1], [0, 1], [0, 0]]),
    geometry.MultiLineString([[[0, 0], [1, 1]], [[1, 0], [0, 1]]]),
    geometry.MultiPolygon([
        geometry.Polygon([[2, 2], [4, 7], [5, 5], [2, 2]]),
        geometry.Polygon([[0, 0], [1, 1], [0, 1], [0, 0]])
    ]),
    Feature(
        geometry=geometry.Polygon([[0, 0], [1, 1], [0, 1], [0, 0]]),
        properties={'a property': 1}
    ),
    FeatureCollection([
        geometry.Polygon([[0, 0], [1, 1], [0, 1], [0, 0]]),
        geometry.Point(0, 0),
        geometry.LineString([[0, 0], [1, 1]])
    ])
)

@ddt.ddt
class TestReprojection(unittest.TestCase):

    "Test reprojection"

    @ddt.data(*GEOMS)
    def test_reprojection(self, geom):
        "Check we can reproject the geometry type"
        output = reproject(geom, from_crs='epsg:3112')
        self.assertIsNotNone(output)
        self.assertEqual(output.geom_type, geom.geom_type)

if __name__ == '__main__':
    unittest.main()
