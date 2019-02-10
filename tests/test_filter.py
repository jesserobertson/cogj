""" file:    test_filter.py (tests)
    author: Jess Robertson, jess@unearthed.solutions
    date:    Sunday, 10 February 2019

    description: Testing filter implementation
"""

import unittest

from shapely import geometry
import ddt
from voluptuous import Schema, Range, Required, All, ALLOW_EXTRA

from cogj import Feature, FeatureCollection, FeatureFilter

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

PROPERTIES = (
    {'id': 1, 'is_multi': False},
    {'id': 2, 'is_multi': True},
    {'id': 3, 'is_multi': False},
    {'id': 4, 'is_multi': False},
    {'id': 5, 'is_multi': True},
    {'id': 6, 'is_multi': True}
)

FEATURES = list(map(lambda args: Feature(geometry=args[0], properties=args[1]),
                    zip(GEOMS, PROPERTIES)))
FCOLLECTION = FeatureCollection(FEATURES)

@ddt.ddt
class TestFilter(unittest.TestCase):

    "Test filtering"

    def test_input_data(self):
        "Check the input data is ok"
        for feature in FCOLLECTION:
            self.assertTrue(isinstance(feature, Feature))
            self.assertIn('id', feature.properties.keys())
            ident = feature.properties['id']
            self.assertTrue(0 < ident < 7)

    @ddt.data(1, 2, 3, 4, 5, 6)
    def test_filter_limit(self, length):
        "Check we can filter with a given limit"
        filt = FeatureFilter(limit=length)
        output = FeatureCollection(filt(FCOLLECTION))
        self.assertEqual(len(output), length)

    @ddt.data(2, 3)
    def test_filter_chunk(self, length):
        "Check we can filter in chunks"
        filt = FeatureFilter(chunk=length)
        for output in filt(FCOLLECTION):
            self.assertEqual(len(output), length)

    def test_filter_schema(self):
        "Check we can filter with a schema"
        schema = Schema({
            Required('id'): All(int, Range(min=2, max=4))
        }, extra=ALLOW_EXTRA)
        filt = FeatureFilter(schema=schema)
        output = FeatureCollection(filt(FCOLLECTION))
        self.assertEqual(len(output), 3)
        for feature in output:
            self.assertTrue(feature.properties['id'] >= 2)
            self.assertTrue(feature.properties['id'] <= 4)

    def test_set_schema(self):
        "Check schema can be set on filter class"
        schema = Schema({
            Required('id'): All(int, Range(min=2, max=4))
        }, extra=ALLOW_EXTRA)
        filt = FeatureFilter(schema=schema)
        filt2 = FeatureFilter()
        filt2.schema = schema
        self.assertEqual(schema, filt.schema)
        self.assertEqual(schema, filt2.schema)
        self.assertEqual(filt.schema, filt2.schema)

    def test_set_schema_dict(self):
        "Check schema can be set on filter class with a dict"
        schema = Schema({
            Required('is_multi'): True
        }, extra=ALLOW_EXTRA)
        filt = FeatureFilter(schema={'is_multi': True})
        filt2 = FeatureFilter()
        filt2.schema = {'is_multi': True}
        self.assertEqual(schema, filt.schema)
        self.assertEqual(schema, filt2.schema)
        self.assertEqual(filt.schema, filt2.schema)

    def test_set_schema_dict_2(self):
        "Check schema can be set on filter class with a dict"
        filt = FeatureFilter(schema={'is_multi': True})
        output = FeatureCollection(filt(FCOLLECTION))
        self.assertEqual(len(output), 3)
        for feature in output:
            self.assertTrue(feature.properties['is_multi'])
            self.assertTrue(feature.properties['id'] in {2, 5, 6})

    def test_filter_no_schema(self):
        "Validation without a schema returns all features"
        filt = FeatureFilter()
        valid = FeatureCollection(filt.validate(FCOLLECTION))
        self.assertEqual(FCOLLECTION, valid)

    def test_filter_all_properties(self):
        "Validation without a schema returns all features"
        filt = FeatureFilter(keep_properties=False)
        for feature in filt(FCOLLECTION):
            self.assertEqual(feature.properties, None)

    def test_filter_no_properties(self):
        "Validation without a schema returns all features"
        filt = FeatureFilter(keep_properties=True)
        for orig, filtered in zip(FCOLLECTION, filt(FCOLLECTION)):
            self.assertEqual(orig, filtered)

    def test_filter_subset_properties(self):
        "Validation without a schema returns all features"
        filt = FeatureFilter(keep_properties=('id',))
        for orig, filtered in zip(FCOLLECTION, filt(FCOLLECTION)):
            self.assertEqual(orig.properties['id'], filtered.properties['id'])
            self.assertNotIn('is_multi', filtered.properties.keys())

    def test_filter_single_property(self):
        "Validation without a schema returns all features"
        filt = FeatureFilter(keep_properties='id')
        for orig, filtered in zip(FCOLLECTION, filt(FCOLLECTION)):
            self.assertEqual(orig.properties['id'], filtered.properties['id'])
            self.assertNotIn('is_multi', filtered.properties.keys())

if __name__ == '__main__':
    unittest.main()
