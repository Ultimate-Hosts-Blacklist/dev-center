"""
The tool to update the input repositories of the Ultimate-Hosts-Blacklist project.

Provides everything around the multiprocessing tester.

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
from itertools import chain
from multiprocessing import active_children
from multiprocessing.managers import BaseManager

import PyFunceble

from ..config import Outputs
from .base import TesterBase


class AutoContinue:
    """
    Provides our shared instance of the AutoContinue subsystem of
    PyFunceble.
    """

    def __init__(self):
        self.auto_continue = PyFunceble.engine.AutoContinue(
            "api_call", parent_process=False
        )

    def add(self, subject, status):
        """
        A wrapper of the :code:`add` method
        """

        self.auto_continue.add(subject, status)

    def get_already_tested(self):
        """
        A wrapper of the :code:`get_already_tested` method
        """

        return self.auto_continue.get_already_tested()

    def get_database(self):
        """
        Provides the database.
        """

        return self.auto_continue.database


class InactiveDB:
    """
    Provides our shared instance of the InactiveDB subsystem of
    PyFunceble.
    """

    def __init__(self):
        self.inactive_db = PyFunceble.database.Inactive(
            "api_call", parent_process=False
        )

    def get_already_tested(self):
        """
        A wrapper of the :code:`get_already_tested` method
        """

        return self.inactive_db.get_already_tested()

    def get_to_retest(self):
        """
        A wrapper of the :code:`get_to_retest` method
        """

        return self.inactive_db.get_to_retest()

    def add(self, subject, status):
        """
        A wrapper of the :code:`add` method
        """

        self.inactive_db.add(subject, status)

    def get_database(self):
        """
        Provides the database.
        """

        return self.inactive_db.database


class Multiprocess(TesterBase):
    """
    Provides the multiprocessing testing mode.
    """

    def __process_test(self, subject, api_core, auto_continue, inactive_db):
        """
        Process the actual test.
        """

        if not self.should_it_be_ignored(subject, auto_continue, inactive_db):
            process = PyFunceble.core.multiprocess.OurProcessWrapper(
                target=self.test, args=(subject, api_core, auto_continue, inactive_db)
            )
            process.name = f"Ultimate {subject}"
            process.start()
        else:
            print(".", end="")

    def test_file(self, file_stream, auto_continue, inactive_db):
        """
        Tests the given file stream.
        """

        while True:
            while (
                len(active_children()) <= self.processes
                and self.are_we_allowed_to_continue()
            ):
                try:
                    for subject in PyFunceble.get_complements(
                        next(file_stream).strip(), include_given=True
                    ):
                        self.__process_test(
                            subject, self.api_core, auto_continue, inactive_db
                        )
                except StopIteration:
                    self.administration.currently_under_test = False
                    break

            self.check_exception(active_children())

            while (
                len(active_children()) >= self.processes
                and "ultimate"
                in " ".join([x.name for x in reversed(active_children())]).lower()
            ):
                logging.debug(
                    "Still active: %s", [x.name for x in reversed(active_children())]
                )

            if (
                not self.administration.currently_under_test
                or not self.are_we_allowed_to_continue()
            ):
                while (
                    "ultimate"
                    in " ".join([x.name for x in reversed(active_children())]).lower()
                ):
                    continue

                break

    def start(self):
        """
        Starts the process.
        """

        BaseManager.register("AutoContinue", AutoContinue)
        BaseManager.register("InactiveDB", InactiveDB)
        manager = BaseManager()

        manager.start()

        auto_continue = manager.AutoContinue()  # pylint: disable=no-member
        inactive_db = manager.InactiveDB()  # pylint: disable=no-member

        with open(
            Outputs.input_destination, "r", encoding="utf-8"
        ) as input_file_stream:
            self.test_file(input_file_stream, auto_continue, inactive_db)

        if not self.administration.currently_under_test:
            self.administration.currently_under_test = True
            self.test_file(
                chain(inactive_db.get_to_retest()), auto_continue, inactive_db
            )

        self.auto_continue.database = PyFunceble.helpers.Merge(
            auto_continue.get_database()
        ).into(self.auto_continue.database)
        self.api_core.inactive_db.database = PyFunceble.helpers.Merge(
            inactive_db.get_database()
        ).into(self.api_core.inactive_db.database)
