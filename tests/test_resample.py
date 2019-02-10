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
from shapely.geometry import shape

from cogj import resample

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
