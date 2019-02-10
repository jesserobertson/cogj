""" file:    test_features.py (tests)
    author: Jess Robertson, jess@unearthed.solutions
    date:    Sunday, 10 February 2019

    description: Tests for feature objects
"""

import unittest

import ddt
from shapely import geometry

from cogj.feature import Feature, FeatureCollection

GEOMS = (
    geometry.Point(0, 0),
    geometry.MultiPoint([[0, 0], [1, 1]]),
    geometry.LineString([[0, 0], [1, 1]]),
    geometry.Polygon([[0, 0], [1, 1], [0, 1], [0, 0]]),
    geometry.MultiLineString([[[0, 0], [1, 1]], [[1, 0], [0, 1]]]),
    geometry.MultiPolygon([
        geometry.Polygon([[2, 2], [4, 7], [5, 5], [2, 2]]),
        geometry.Polygon([[0, 0], [1, 1], [0, 1], [0, 0]])
    ])
)

JSON = (
    '{"type": "Feature", "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}, '
        '"properties": null}',
    '{"type": "Feature", "geometry": {"type": "MultiPoint", '
        '"coordinates": [[0.0, 0.0], [1.0, 1.0]]}, "properties": null}',
    '{"type": "Feature", "geometry": {"type": "LineString", '
        '"coordinates": [[0.0, 0.0], [1.0, 1.0]]}, "properties": null}',
    '{"type": "Feature", "geometry": {"type": "Polygon", '
        '"coordinates": [[[0.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]]]}, "properties": null}',
    '{"type": "Feature", "geometry": {"type": "MultiLineString", '
        '"coordinates": [[[0.0, 0.0], [1.0, 1.0]], [[1.0, 0.0], [0.0, 1.0]]]}, "properties": null}',
    '{"type": "Feature", "geometry": {"type": "MultiPolygon", '
        '"coordinates": [[[[2.0, 2.0], [4.0, 7.0], [5.0, 5.0], [2.0, 2.0]]], '
        '[[[0.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]]]]}, "properties": null}',
)

@ddt.ddt
class TestFeature(unittest.TestCase):

    "Test Feature behaviour"

    @ddt.data(*GEOMS)
    def test_setup(self, geom):
        "Check we can create an empty object"
        feature = Feature(geom)
        self.assertIsNone(feature.properties)
        self.assertEqual(feature.geometry, geom)

    @ddt.data(*GEOMS)
    def test_equality(self, geom):
        "Test equality"
        feat1 = Feature(geom, {'a property': 1})
        feat2 = Feature(geom, {'a property': 1})
        self.assertEqual(feat1, feat2)

    @ddt.data(*zip(GEOMS, JSON))
    @ddt.unpack
    def test_json(self, geom, expected):
        "Check JSON output"
        feat = Feature(geom)
        self.assertEqual(feat.json(), expected)

@ddt.ddt
class TestFeatureCollection(unittest.TestCase):

    "Test FeatureCollection behaviour"

    def test_setup(self):
        "Check we can create an empty object"
        collection = FeatureCollection(GEOMS)
        for geom, feat in zip(GEOMS, collection.features):
            self.assertEqual(feat.geometry, geom)
        for geom, cgeom in zip(GEOMS, collection.geometries):
            self.assertEqual(geom, cgeom)

    def test_equality(self):
        "Test equality"
        coll1 = FeatureCollection(GEOMS)
        coll2 = FeatureCollection(GEOMS)
        self.assertEqual(coll1, coll2)

    def test_iter(self):
        "Iteration should be over features"
        feats = map(Feature, GEOMS)
        coll = FeatureCollection(GEOMS)
        for feat1, feat2 in zip(coll, feats):
            self.assertEqual(feat1, feat2)

if __name__ == '__main__':
    unittest.main()