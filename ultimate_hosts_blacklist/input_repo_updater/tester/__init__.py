"""
The tool to update the input repositories of the Ultimate-Hosts-Blacklist project.

Provides the tester.

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
from datetime import datetime, timedelta
from os import cpu_count

import PyFunceble

import ultimate_hosts_blacklist.input_repo_updater as launcher

from ..authorization import Authorization
from .base import TesterBase
from .multiprocess import Multiprocess
from .single import Single


class Tester(TesterBase):
    """
    Process the test.
    """

    def __init__(self, multiprocessing):
        super().__init__()
        self.multiprocessing = multiprocessing

        logging.info("Multiprocessing: %s", self.multiprocessing)
        logging.info("Allowed Processes: %s", self.processes)

        if not self.multiprocessing:
            Single().start()
        else:
            Multiprocess().start()

        self.save_all()
