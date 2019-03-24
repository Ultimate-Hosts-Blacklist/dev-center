"""
The tool to update the input repositories of the Ultimate-Hosts-Blacklist project.

Provide the authorization logic.

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
from ultimate_hosts_blacklist.input_repo_updater.configuration import Infrastructure
from ultimate_hosts_blacklist.helpers import Regex, Command
from ultimate_hosts_blacklist.input_repo_updater import logging
from time import time
from ultimate_hosts_blacklist.input_repo_updater.pyfunceble import PyFunceble
from tempfile import gettempdir


class Authorization:
    """
    Provide the authorization for a test.

    If needed, this class automatically clean the output directory.
    If needed, we download the latest version of upstream.
    """

    authorized = False
    cleaned = False

    def __init__(self, administration_data):
        self.__administration_data = administration_data
        self.get()

    def __launch_test(self):
        """
        Provide the launch test handler.
        """

        return Regex(
            Command("git log -1", allow_stdout=False).execute(),
            Infrastructure.markers["launch_test"],
            return_data=False,
        ).match()

    def __currently_under_test(self):
        """
        Provide the currently under test handler.
        """

        return self.__administration_data["currently_under_test"]

    def get(self):
        """
        Provide or deny the authorization.
        """

        if self.__launch_test():
            self.authorized = True
            logging.info(
                "Test authorized by: {0}.".format(
                    repr(Infrastructure.markers["launch_test"])
                )
            )

            # TODO: Implement the cleaning logic.
        elif self.__currently_under_test():
            self.authorized = True
            self.cleaned = False

            logging.info("Test authorized by: Still under test.")
        elif not self.__currently_under_test():
            self.authorized = True
            self.cleaned = True

            PyFunceble.clean()
            logging.info("Test authorized by: Not currently under test.")
        elif (
            self.__administration_data["days_until_next_test"] >= 1
            and self.__administration_data["last_test"] != 0
        ):
            expected_retest_date = (
                24 * self.__administration_data["days_until_next_test"] * 3600
            )

            if int(time()) >= expected_retest_date:
                self.authorized = True
                self.cleaned = True

                PyFunceble.clean()
                logging.info("Test authorized by: Restest time in the past.")
            else:
                self.authorized = self.cleaned = False
                logging.info("Test not authorized by: Retest time in the future.")
        else:
            raise Exception("Unable to determine authorization.")

        return self.authorized

