"""
The tool to update the input repositories of the Ultimate-Hosts-Blacklist project.

Provides everything around the single mode tester.

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

from itertools import chain

import PyFunceble

from ..config import Outputs
from .base import TesterBase


class Single(TesterBase):
    """
    Provides the single mode tester.
    """

    def __process_test(self, subject):
        """
        Process the actual test.
        """

        if not self.should_it_be_ignored(
            subject, self.auto_continue, self.api_core.inactive_db
        ):
            self.test(
                subject,
                self.api_core,
                self.auto_continue,
                self.api_core.inactive_db,
                self.api_core.whois_db,
            )
        else:
            print(".", end="")

    def test_file(self, file_stream):
        """
        Tests the content of the given file.
        """

        while self.are_we_allowed_to_continue():
            try:
                for subject in PyFunceble.get_complements(
                    next(file_stream).strip(), include_given=True
                ):
                    self.__process_test(subject)
            except StopIteration:
                self.administration.currently_under_test = False
                break

    def start(self):
        """
        Starts the process.
        """

        with open(
            Outputs.input_destination, "r", encoding="utf-8"
        ) as input_file_stream:
            self.test_file(input_file_stream)

        if not self.administration.currently_under_test:
            self.administration.currently_under_test = True
            self.test_file(chain(self.api_core.inactive_db.get_to_retest()))
