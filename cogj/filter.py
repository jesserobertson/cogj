""" file:   filter.py (cogj)
    author: Jess Robertson, @jesserobertson
    date:   Sunday, 27 January 2019

    description: Functions to filter vector data
"""

from collections import Iterable

import voluptuous
from toolz.curried import take, compose

from .feature import Feature
from .logging import LoggerMixin
from .utilities import grouper

class FeatureFilter(LoggerMixin):

    """
    Handles vector geospatial data with some lazy filtering of records
    """

    def __init__(self, limit=None, schema=None, keep_properties=True, chunk=False):
        self.schema = schema
        self.limit = limit
        self.keep_properties = keep_properties
        self.chunk = chunk or False

        # Set up pipeline, in reverse order
        steps = [self.validate, self.process]
        if self.limit is not None:
            self.logger.debug(f'Loading %s records only', self.limit)
            steps.append(take(self.limit))
        if self.chunk:
            self.logger.debug(f'Records will arrive in batches of %s', self.chunk)
            steps.append(lambda it: grouper(self.chunk, it))
        self.pipeline = compose(*reversed(steps))

    def __call__(self, records):
        "Filter records using the schema"
        yield from self.pipeline(records)

    @property
    def schema(self):
        "Get current schema"
        return self._schema

    @schema.setter
    def schema(self, new_schema):
        "Set new schema. If None then schema is removed"
        try:
            self._schema = voluptuous.Schema(new_schema) if new_schema else None  # pylint: disable=W0201
        except voluptuous.Invalid as err:
            self.logger.error('Something went wrong importing new schema')
            self.logger.error('Error message from voluptuous follows:')
            self.logger.error('%s', err)
            raise err

    def validate(self, records):
        """
        Lazily evaulate an iterator against a given schema. Objects which fail
        to validate are skipped.

        Parameters:
            records - an iterator of records to validate

        Returns:
            an iterator of valid values
        """
        if self.schema is None:
            self.logger.info('No schema, returning all records')
            yield from records
        else:
            self.logger.info('Validating records against schema')
            for item in records:
                try:
                    if isinstance(item, Feature):
                        self._schema(item.properties)  # validate
                        yield item
                    else:
                        yield self._schema(item)
                except voluptuous.MultipleInvalid:
                    self.logger.debug('Skipping invalid object %s', item)
                    continue
                except AttributeError:
                    raise ValueError('No schema set for filter')

    def process(self, records):
        """
        Process properties dictionaries

        Sometimes we don't want to keep all the properties in a vector format in the final
        dataset (especially if we've already filtered out what we don't care about).
        This method filters on the self.keep_properties attribute.

        Parameters:
            records - an iterator of feature records

        Returns:
            an iterator over filtered records with properties handled
        """
        if isinstance(self.keep_properties, Iterable):
            _keep_properties = set(self.keep_properties)
            self.logger.debug("Keeping a subset of records: %s", _keep_properties)
            for record in records:
                record['properties'] = {k: v for k, v in record['properties'].items()
                                        if k in _keep_properties}
                yield record
        elif self.keep_properties:
            self.logger.debug("Keeping all properties from records")
            yield from records
        else:
            self.logger.debug("Removing all properties from records")
            for record in records:
                record['properties'] = {}
                yield record
