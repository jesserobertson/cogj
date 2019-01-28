""" file:   logging.py (cogj)
    author: Jess Robertson, @jesserobertson
    date:   June 2018

    description: Mixin class to give classes loggers
"""

import logging

class LoggerMixin:  # pylint: disable=R0903

    """
    Mixin class to add logging to a class

    Adds a logger property which contains an automatically configured logger
    """

    @property
    def logger(self):
        "Return a logger instance"
        try:
            return self._logger
        except AttributeError:
            # We haven't initialized the logger yet
            name = '.'.join((
                self.__module__,
                self.__class__.__name__))
            self._logger = logging.getLogger(name)
            return self._logger
