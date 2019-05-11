"""
The tool to update the input repositories of the Ultimate-Hosts-Blacklist project.

The main entry of the tool.

License:
::


    MIT License

    Copyright (c) 2019 Ultimate-Hosts-Blacklist
    Copyright (c) 2019 Nissar Chababy
    Copyright (c) 2019 Mitchell Krog

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""
import argparse
import logging

from colorama import Fore, Style
from colorama import init as initiate_coloration
from ultimate_hosts_blacklist.input_repo_updater.core import Core

VERSION = "1.6.0"


def _command_line():
    """
    Provides the CLI.
    """

    if __name__ == "ultimate_hosts_blacklist.input_repo_updater":
        initiate_coloration(autoreset=True)

        parser = argparse.ArgumentParser(
            description="The tool to update the input repositories of the Ultimate-Hosts-Blacklist project.",  # pylint: disable=line-too-long
            epilog="Crafted with %s by %s"
            % (
                Fore.RED + "♥" + Fore.RESET,
                Style.BRIGHT + Fore.CYAN + "Nissar Chababy (Funilrys)",
            ),
        )

        parser.add_argument(
            "-d",
            "--debug",
            help="Write all debug information to stdout.",
            action="store_true",
            default=False,
        )

        parser.add_argument(
            "-m",
            "--multiprocess",
            help="Activate the usage of multiple processes.",
            action="store_true",
            default=False,
        )

        parser.add_argument(
            "-v",
            "--version",
            help="Show the version end exist.",
            action="version",
            version="%(prog)s " + VERSION,
        )

        arguments = parser.parse_args()

        if arguments.debug:
            logging_level = logging.DEBUG
        else:
            logging_level = logging.INFO

        Core(
            logging_level=logging_level, multiprocessing=arguments.multiprocess
        ).process()
