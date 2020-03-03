"""
The tool to update the input repositories of the Ultimate-Hosts-Blacklist project.

Provides the cleaner of the PyFunceble Infrastructur.

License:
::


    MIT License

    Copyright (c) 2019, 2020  Ultimate-Hosts-Blacklist
    Copyright (c) 2019, 2020  Nissar Chababy
    Copyright (c) 2019, 2020  Mitchell Krog

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

import logging

import PyFunceble

from ..config import Outputs
from .base import CleanerBase


class PyFuncebleCleaner(CleanerBase):
    """
    Cleans everything which is related to PyFunceble and that we do not need.
    """

    to_delete = [
        Outputs.output_destination + Outputs.continue_filename,
        Outputs.current_directory + "dir_structure.json",
        Outputs.current_directory + "dir_structure_production.json",
    ]

    def __init__(self, authorization):
        self.__official_auth = authorization
        super().__init__()

    def authorization(self):
        return self.__official_auth.get_cleaning_authorization()

    def start(self):
        logging.info(
            "Authorized to clean the PyFunceble's infrastructure: %s", self.authorized
        )

        for file in self.to_delete:
            logging.info("Deletion of %s", repr(file))

            PyFunceble.helpers.File(file).delete()

        # We now clean everything actually related to PyFunceble
        PyFunceble.load_config(generate_directory_structure=False)
        PyFunceble.output.Clean()
