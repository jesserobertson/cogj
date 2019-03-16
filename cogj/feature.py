""" file:    feature.py (cogj)
    author: Jess Robertson, jess@unearthed.solutions
    date:    Sunday, 27 January 2019

    description: Feature and FeatureCollection implementation - to make it easier to
        to work with GeoJSON and Shapely objects
"""

import json

from shapely.geometry import mapping

from .identity import IdentityMixin

class Feature(IdentityMixin):

    "GeoJSON Feature object"

    geom_type = 'Feature'

    def __init__(self, geometry, properties=None):
        self.geometry = geometry
        self.properties = properties

    @property
    def __geo_interface__(self):
        return {
            "type": "Feature",
            "geometry": self.geometry.__geo_interface__,
            "properties": self.properties
        }

    def __eq__(self, other):
        "Two features are equal if their representations are equal"
        return self.__geo_interface__ == other.__geo_interface__

    def json(self, compact=False, **kwargs):
        """
        Serialize to JSON

        Parameters:
            kwargs - get passed to `jaon.dumps`. Useful for pretty-printing
        """
        if compact:
            kwargs.update(separators=(',', ':'))
        return json.dumps(mapping(self), **kwargs)


class FeatureCollection:

    """
    GeoJSON FeatureCollection object

    Collects together features into a set. Provides an iterator over features
    or shapes via geometries or self.

    Parameters:
        objects - either `shapely.geometry` or `cogj.Feature` objects. Shapes
            are transformed to Features internally
    """

    geom_type = 'FeatureCollection'

    def __init__(self, objects):
        objects = list(objects)
        if all(isinstance(f, Feature) for f in objects):
            self.features = objects
        else:
            try:
                self.features = [Feature(g) for g in objects]
            except ValueError:
                raise ValueError('Features must be cogj.Feature or shapely geometry')

    @property
    def geometries(self):
        "Return iterator over feature geometries"
        for feature in self.features:
            yield feature.geometry

    @property
    def __geo_interface__(self):
        return {
            "type": "FeatureCollection",
            "features": [f.__geo_interface__ for f in self.features]
        }

    def __len__(self):
        return len(self.features)

    def __iter__(self):
        return iter(self.features)

    def __eq__(self, other):
        "Two FeatureCollections are equal if their representations are equal"
        return self.__geo_interface__ == other.__geo_interface__

    def json(self, compact=False, **kwargs):
        """
        Serialize to JSON

        Parameters:
            kwargs - get passed to `jaon.dumps`. Useful for pretty-printing
        """
        if compact:
            kwargs.update(separators=(',', ':'))
        return json.dumps(mapping(self), **kwargs)
