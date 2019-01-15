""" file:    main.py (cli)
    author: Jess Robertson, jess@unearthed.solutions
    date:    Tuesday, 15 January 2019

    description: Top-level API for cogj tool
"""

import logging

import click
import click_log

from .info import info_command
from .convert import convert_command

# Logger options
LOGGER = logging.getLogger('cogj')
click_log.basic_config(LOGGER)

@click.group('cogj')
@click_log.simple_verbosity_option(LOGGER)
def cogj():
    """\b
       _|_|_|    _|_|      _|_|_|  _|_|_|_|     | Cloud-optimized GeoJSON tools
     _|        _|    _|  _|              _|     | WFS without the WTF
     _|        _|    _|  _|  _|_|        _|     |
     _|        _|    _|  _|    _|  _|    _|     | Developed by Jess Robertson (@jesserobertson)
       _|_|_|    _|_|      _|_|_|    _|_|       | January 2019

    For more info, try `cogj COMMAND --help`
    """
    LOGGER.debug('COGJ up and running!')

cogj.add_command(info_command)
cogj.add_command(convert_command)

if __name__ == '__main__':
    cogj()
