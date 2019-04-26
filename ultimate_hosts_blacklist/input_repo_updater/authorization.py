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
# pylint: disable=bad-continuation
from time import time

from ultimate_hosts_blacklist.helpers import Command, Regex
from ultimate_hosts_blacklist.input_repo_updater import logging
from ultimate_hosts_blacklist.input_repo_updater.configuration import Infrastructure
from ultimate_hosts_blacklist.input_repo_updater.domains_list import DomainsList


class Authorization:  # pylint: disable=too-few-public-methods
    """
    Provide the authorization for a test.

    If needed, this class automatically clean the output directory.
    If needed, we download the latest version of upstream.

    :param dict administration data: The fomatted content of the administration file.
    """

    # Save the authorization to run.
    authorized = False
    # Save the cleaning part.
    clean = False

    def __init__(self, administration_data, shared_pyfunceble=None):
        self._administration_data = administration_data
        self.shared_pyfunceble = shared_pyfunceble
        self.get()

    @classmethod
    def __launch_test(cls):
        """
        Provide the launch test handler.
        """

        return Regex(
            Command("git log -1", allow_stdout=False).execute(),
            Infrastructure.markers["launch_test"],
            return_data=False,
        ).match()

    def __is_currently_under_test(self):
        """
        Provide the currently under test handler.
        """

        return self._administration_data["currently_under_test"]

    def get(self):
        """
        Provide or deny the authorization.
        """

        if self.__launch_test():
            # The launch test marker was send by a maintainer or
            # member of the team.

            # We authorize the test.
            self.authorized = True

            # And we "force" the cleaning.
            self.clean = True

            # We download/format the raw link/domains.list file.
            DomainsList(
                self._administration_data["raw_link"],
                shared_pyfunceble=self.shared_pyfunceble,
            )
            logging.info(
                "Test authorized by: {0}.".format(
                    repr(Infrastructure.markers["launch_test"])
                )
            )
        elif self.__is_currently_under_test():
            # We are still under test.

            # We authorize the test.
            self.authorized = True
            # But we do not authorize the cleaning.
            self.clean = False

            logging.info("Test authorized by: Still under test.")
        elif not self.__is_currently_under_test():
            # We are not under test.

            # We authorize the test.
            self.authorized = True
            # We "force" the cleaning.
            self.clean = True

            # We download/format the raw link/domains.list file.
            DomainsList(
                self._administration_data["raw_link"],
                shared_pyfunceble=self.shared_pyfunceble,
            )
            logging.info("Test authorized by: Not currently under test.")
        elif (
            int(self._administration_data["days_until_next_test"]) >= 1
            and int(self._administration_data["last_test"]) >= 0
        ):
            # * The given days until next next is >= 1.
            # and
            # * The last test time is >= 0

            # We calculate the expected retest date.
            expected_retest_date = (
                24 * self._administration_data["days_until_next_test"] * 3600
            )

            if int(time()) >= expected_retest_date:
                # The expected retest date is in the past.

                # We authorize the test.
                self.authorized = True
                # We "force" the cleaning.
                self.clean = True

                # We download/format the raw link/domains.list file.
                DomainsList(
                    self._administration_data["raw_link"],
                    shared_pyfunceble=self.shared_pyfunceble,
                )
                logging.info("Test authorized by: Restest time in the past.")
            else:
                # The expected retest date is in th efuture.

                # We do not authorize the test.
                self.authorized = self.clean = False
                logging.info("Test not authorized by: Retest time in the future.")
        else:
            raise Exception("Unable to determine authorization.")

        return self.authorized
