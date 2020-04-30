"""
The tool to update the input repositories of the Ultimate-Hosts-Blacklist project.

Provides the base of all installer.

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
import sys

import PyFunceble
from PyFunceble.helpers import EnvironmentVariable

from ultimate_hosts_blacklist.helpers import Command

from ..administration import Administration
from ..config import Infrastructure, OurPyFuncebleConfig, Outputs


class InstallerBase:
    """
    Provides the base class of all installer.
    """

    def __init__(self):
        self.administration = Administration()

        self.pyfunceble_version = self.get_pyfunceble_version_to_use()
        self.infrastructure_version = self.get_infrstructure_version_to_use()

        config_info = getattr(Infrastructure, f"links_{self.infrastructure_version}")[
            "config"
        ]
        self.pyfunceble_cross_destination = (
            f"{Outputs.current_directory}{config_info['cross_destination']}"
        )
        self.pyfunceble_destination = (
            f"{Outputs.current_directory}{config_info['destination']}"
        )

        self.authorized = self.authorization()

        if self.authorized and not hasattr(self, "dont_start"):
            self.start()

        if not hasattr(self, "dont_start"):
            self.administration.save()

    def authorization(self):
        """
        Provides the authorization to process.
        """

        raise NotImplementedError()

    def start(self):
        """
        Start the installation process.
        """

        raise NotImplementedError()

    @classmethod
    def init_ci(cls):
        """
        Initiates the CI environment.
        """

        ci_engine = PyFunceble.engine.AutoSave.get_current_ci()

        if ci_engine:
            ci_engine.init()

    @classmethod
    def check_changes_and_commit(cls, file_to_check, commit_message=None):
        """
        Checks if the given :code:`file_to_check` has been changed and process
        the commit, push and exit of the tool.
        """

        branch = EnvironmentVariable("GIT_BRANCH")
        if branch.exists() and EnvironmentVariable("TRAVIS_BUILD_DIR"):
            if (
                Command(f"git status --porcelain {file_to_check}", allow_stdout=False)
                .execute()
                .strip()
                .startswith("M")
            ):
                logging.info("Stopping instance: %s", commit_message)
                cls.init_ci()

                Command(
                    "git add {0} && git commit -m '{1}' && git push origin {2}".format(
                        file_to_check, commit_message, branch.get_value()
                    )
                ).execute()

                sys.exit(0)

    def get_pyfunceble_version_to_use(self):
        """
        Provides the name of the pyfunceble version to use.
        """

        if (
            "pyfunceble_version" in self.administration
            and OurPyFuncebleConfig.is_package_known(
                self.administration.pyfunceble_version
            )
        ):
            return self.administration.pyfunceble_version
        return OurPyFuncebleConfig.default_package

    def get_infrstructure_version_to_use(self):
        """
        Provides the name of the infrastructure version to use.
        """

        if (
            "infrastructure_version" in self.administration
            and Infrastructure.is_version_known(
                self.administration.infrastructure_version
            )
        ):
            return self.administration.infrastructure_version
        return Infrastructure.default_version
