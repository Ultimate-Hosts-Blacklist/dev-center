"""
The tool to update the input repositories of the Ultimate-Hosts-Blacklist project.

Provides the global authorization logic.

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

from PyFunceble.helpers import Regex

from ultimate_hosts_blacklist.helpers import Command

from .administration import Administration
from .config import Infrastructure
from .domains_list import DomainsList
from .exceptions import UnableToAuthorize


class Authorization:
    """
    Provide the authorization for a test.

    If needed, this class automatically clean the output directory.
    If needed, we download the latest version of upstream.

    :param dict administration data: The fomatted content of the administration file.
    """

    authorized = False
    clean = False

    def __init__(self):
        self.adminstration = Administration()
        self.authorized, self.clean = self.__get()

        del self.adminstration

    @classmethod
    def __launch_test(cls):
        """
        Provide the launch test handler.
        """

        return Regex(Infrastructure.markers["launch_test"]).match(
            Command("git log -1", allow_stdout=False).execute(), return_match=False
        )

    def __is_currently_under_test(self):
        """
        Provide the currently under test handler.
        """

        return self.adminstration.currently_under_test

    def __get(self):
        """
        Provide or deny the authorization.
        """

        DomainsList(self.adminstration.raw_link).generate()

        if self.__launch_test():
            authorized = True
            clean = True

            logging.info(
                "Test authorized by: %s.", repr(Infrastructure.markers["launch_test"])
            )
        elif self.__is_currently_under_test():
            authorized = True
            clean = False

            logging.info("Test authorized by: Still under test.")
        elif not self.__is_currently_under_test():
            authorized = True
            clean = True

            logging.info("Test authorized by: Not currently under test.")
        elif int(self.adminstration.days_until_next_test) >= 1:
            expected_retest_date = datetime.now() + timedelta(
                days=self.adminstration.days_until_next_test
            )

            if datetime.now() >= expected_retest_date:
                authorized = True
                clean = True

                logging.info("Test authorized by: Restest time in the past.")
            else:
                authorized = clean = False
                logging.info("Test not authorized by: Retest time in the future.")
        else:
            raise UnableToAuthorize()

        return authorized, clean

    def get_cleaning_authorization(self):
        """
        Provides the cleaning authorization
        """

        return self.clean

    def get_authorization(self):
        """
        Provides the authorizsation to launch a test.
        """

        return self.authorized
