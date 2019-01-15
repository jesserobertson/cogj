""" file:    main.py (cli)
    author: Jess Robertson, jess@unearthed.solutions
    date:    Tuesday, 15 January 2019

    description: Top-level API for cogj tool
"""

import logging

import click
import click_log

# Logger options
LOGGER = logging.getLogger('cogj')
click_log.basic_config(LOGGER)

@click.group('cogj')
@click_log.simple_verbosity_option(LOGGER)
def main():
    """\b
       _|_|_|    _|_|      _|_|_|  _|_|_|_|     | Cloud-optimized GeoJSON tools
     _|        _|    _|  _|              _|     | WFS without the WTF
     _|        _|    _|  _|  _|_|        _|     |
     _|        _|    _|  _|    _|  _|    _|     | Developed by Jess Robertson (@jesserobertson)
       _|_|_|    _|_|      _|_|_|    _|_|       | January 2019

    For more info, try `cogj COMMAND --help`
    """
    LOGGER.debug('COGJ up and running!')
