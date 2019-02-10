#!/usr/bin/env python
""" file: test_resample.py
    author: Jess Robertson, @jesserobertson
    date:   Sunday, 27 January 2019

    description: Unit tests for resampler
"""

import unittest
import os
import pathlib

import fiona
from shapely.geometry import shape, Point

from cogj import resample, resample_linestring_count

RESOURCES = pathlib.Path(__file__).parent / 'resources'

def all_close(iter_a, iter_b, tol=1e-6):
    "Check iterables of floats are close in value"
    return all(abs(a - b) < tol for a, b in zip(iter_a, iter_b))

class TestResample(unittest.TestCase):

    "Tests for resampling"

    def setUp(self):
        self.test_data = os.path.join(RESOURCES, 'boundary.json')
        with fiona.open(self.test_data) as src:
            self.poly = shape(src[0]['geometry'])

        # Set up default resampling args
        self.kwargs = dict(
            resolution=0.001,
            clip=[10, 3000],
            return_points=False
        )

    def test_have_data(self):
        "Check that our test data is available"
        self.assertTrue(self.poly is not None)
        self.assertTrue(len(self.poly.boundary.xy) > 0)

    def test_resample_linestring(self):
        "Check we can resample a linestring"
        linestr = self.poly.boundary
        output = resample(linestr, **self.kwargs)
        self.assertTrue(output.geom_type == 'LineString')

        # Check we have actually done a subsample
        len_new = len(output.xy[0])
        len_old = len(linestr.xy[0])
        print(len_new, len_old)
        self.assertTrue(len_old < len_new)

    def test_resample_linestring_count(self):
        "Check we can resample a linestring with a given count"
        linestr = self.poly.boundary
        output = resample_linestring_count(linestr, count=10)
        self.assertTrue(output.geom_type == 'LineString')
        self.assertEqual(len(output.xy[0]), 10)

    def test_resample_linestring_step(self):
        "Check we can resample a linestring with a given step"
        linestr = self.poly.boundary
        output = resample_linestring_count(linestr, step=0.1)
        self.assertTrue(output.geom_type == 'LineString')
        self.assertTrue(len(output.xy[0]) > len(linestr.xy[0]))

    def test_resample_linestring_step_no_round(self):
        "Check we can resample a linestring with a given step"
        linestr = self.poly.boundary
        output = resample_linestring_count(linestr, step=0.1, step_round=False)
        self.assertTrue(output.geom_type == 'LineString')
        self.assertTrue(len(output.xy[0]) > len(linestr.xy[0]))

    def test_resample_linestring_count_step_and_count(self):
        "Specifying both count and step raises an error"
        linestr = self.poly.boundary
        with self.assertRaises(ValueError):
            resample_linestring_count(linestr, step=0.1, count=50)

    def test_resample_linestring_long_step(self):
        "Step length > boundary length is an error"
        linestr = self.poly.boundary
        with self.assertRaises(ValueError):
            resample_linestring_count(linestr, step=1e8, step_round=False)

    def test_resample_nonresample(self):
        "Resampling a non-linestring or polygon is an error"
        geom = Point([0, 0])
        with self.assertRaises(ValueError):
            resample(geom, **self.kwargs)

    def test_resample_polygon(self):
        "Check we can resample a polygon"
        poly = self.poly
        output = resample(poly, **self.kwargs)
        self.assertTrue(output.geom_type == 'Polygon')

        # Check we have actually done a subsample
        len_new = len(output.boundary.xy[0])
        len_old = len(poly.boundary.xy[0])
        self.assertTrue(len_old < len_new)

    def check_points_come_back_the_same(self):
        "Check that points from resampling polygon boundary and" \
        "linestring are exactly the same"
        kwargs = self.kwargs.copy()
        kwargs['return_points'] = True

        # Generate resamples for poly and boundary
        poly = self.poly
        bound = poly.boundary
        pts_poly = resample(poly, **kwargs)
        pts_bound = resample(bound, **kwargs)
        self.assertTrue(all_close(pts_poly, pts_bound))

if __name__ == '__main__':
    unittest.main()
