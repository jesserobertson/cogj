""" file:   filter.py (cogj)
    author: Jess Robertson, @jesserobertson
    date:   Sunday, 27 January 2019

    description: Functions to filter vector data
"""

from collections import Iterable

from voluptuous import Schema, ALLOW_EXTRA, MultipleInvalid
from toolz.curried import take, compose

from .feature import Feature
from .logging import LoggerMixin
from .utilities import grouper

class FeatureFilter(LoggerMixin):

    """
    Handles vector geospatial data with some lazy filtering of features

    Parameters:
        limit - the number of features to keep
        schema - a voluptuous.Schema or dictionary to use to filter on
            feature properties
        keep_properties - if True, all feature properties are kept, if
            False, no feature properties are kept, if an iterable of
            feature keys, only those features are kept
        chunk - if not False, returns the features in chunks of n
    """

    def __init__(self, limit=None, schema=None, keep_properties=True, chunk=False):
        self.schema = schema
        self.limit = limit
        self.chunk = chunk or False
        self.set_property_filter(keep_properties)

        # Set up pipeline, in reverse order
        steps = [self.validate, self.process]
        if self.limit is not None:
            self.logger.debug(f'Loading %s features only', self.limit)
            steps.append(take(self.limit))
        if self.chunk:
            self.logger.debug(f'Features will arrive in batches of %s', self.chunk)
            steps.append(lambda it: grouper(self.chunk, it))
        self.pipeline = compose(*reversed(steps))

    def __call__(self, features):
        "Filter features using the schema"
        yield from self.pipeline(features)

    def set_property_filter(self, keep_properties=False):
        "Set keep_properties attribute"
        if isinstance(keep_properties, str):
            self._process_properties = lambda f: \
                self._filter_properties({keep_properties,}, f)
        elif isinstance(keep_properties, Iterable):
            self._process_properties = lambda f: \
                self._filter_properties(set(keep_properties), f)
        elif keep_properties:
            self._process_properties = self._allow_properties
        else:
            self._process_properties = self._remove_properties

    @property
    def schema(self):
        "Get current schema"
        return self._schema

    @schema.setter
    def schema(self, new_schema):
        "Set new schema. If None then schema is removed"
        if new_schema is not None and not isinstance(new_schema, Schema):
            new_schema = Schema(new_schema, extra=ALLOW_EXTRA)
        self.logger.debug('Updating schema to %s', new_schema)
        self._schema = new_schema  # pylint: disable=W0201

    def validate(self, features):
        """
        Lazily evaulate an iterator against a given schema. Objects which fail
        to validate are skipped.

        Parameters:
            features - an iterator of features to validate

        Returns:
            an iterator of valid values
        """
        if self._schema is None:
            self.logger.info('No schema, returning all features')
            yield from features
            return

        self.logger.info('Validating features against schema')
        for feature in features:
            try:  # validation
                self._schema(feature.properties)
                yield feature
            except MultipleInvalid as err:
                self.logger.debug('Skipping invalid object %s', feature)
                self.logger.debug('Errors: %s', err.errors)
                continue

    def process(self, features):
        """
        Process properties dictionaries

        Sometimes we don't want to keep all the properties in a vector format in the final
        dataset (especially if we've already filtered out what we don't care about).
        This method filters on the self.keep_properties attribute.

        Parameters:
            features - an iterator of feature features

        Returns:
            an iterator over filtered features with properties handled
        """
        for feature in features:
            yield self._process_properties(feature)

    def _allow_properties(self, feature):
        "Allow all features"
        self.logger.debug("Keeping all properties from features")
        return feature

    def _remove_properties(self, feature):
        "Remove properties from feature"
        self.logger.debug("Removing all properties from features")
        return Feature(geometry=feature.geometry)

    def _filter_properties(self, keep, feature):
        "Process removing some features"
        self.logger.debug("Keeping a subset of features: %s", keep)
        return Feature(
            geometry=feature.geometry,
            properties={
                k: v for k, v in feature.properties.items()
                if k in keep
            })
