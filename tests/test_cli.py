#!/usr/bin/env python
""" file:    test_cli.py (tests)
    author: Jess Robertson, jess@unearthed.solutions
    date:    Tuesday, 15 January 2019

    description: Tests for CLI
"""

import unittest
import logging
import sys
import shlex
import pathlib

import ddt
from click.testing import CliRunner

# Add CLI folder to our current PYTHONPATH so we can load the CLI
CLI_LOCATION = pathlib.Path(__file__).parent.parent / 'cogj'
sys.path.insert(0, str(CLI_LOCATION))  # Push folder to front of path

# This needs to go after pythonpath munging
from cogj.cli import main as cli

LOGGER = logging.getLogger('cogj')

@ddt.ddt
class TestCLI(unittest.TestCase):
    """ Test main CLI functions
    """

    def setUp(self):
        self.runner = CliRunner()

    def run_command(self, command=None):
        """ Run a command throught the CLI
        """
        # Parse arguments
        if command:
            if isinstance(command, str):
                args = shlex.split(command)
            elif isinstance(command, list):
                args = command
            else:
                msg = "Arguments to run_command couldn't be parsed"
                LOGGER.error(msg)
                raise ValueError(msg)
        else:
            args = []

        if args and args[0] == 'cogj':
            args = args[1:]
        result = self.runner.invoke(cli, args)

        # Make sure that things exited ok
        if result.exit_code != 0:
            LOGGER.error('CLI exited abnormally with exit code %s!',
                         result.exit_code)
            LOGGER.info(f'CLI output: {result.output}')
            LOGGER.info(f'Invoked with: cogj' + ' '.join(args))

        return result

    def test_help(self):
        "Check help message comes through ok"
        result = self.run_command('cogj')
        print(result.output)
        self.assertTrue('Usage: cogj [OPTIONS] COMMAND [ARGS' in result.output)

    def test_verbose(self):
        "Check verbosity options"
        result = self.run_command('cogj -v DEBUG --help')
        self.assertTrue('debug: COGJ up and running!' in result.output)

if __name__ == '__main__':
    unittest.main()