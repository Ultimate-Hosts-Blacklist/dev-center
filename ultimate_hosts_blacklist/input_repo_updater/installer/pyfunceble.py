"""
The tool to update the input repositories of the Ultimate-Hosts-Blacklist project.

The PyFunceble installer. Installs everything related to PyFunceble.

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

from PyFunceble.helpers import Download, File

from ..config import Infrastructure, OurPyFuncebleConfig, Outputs
from ..exceptions import CouldNotDownload
from .base import InstallerBase


class PyFuncebleInstaller(InstallerBase):
    """
    Provides tthe installer of everything around PyFunceble.
    """

    def authorization(self):
        return not File(self.pyfunceble_cross_destination).exists()

    def install_config(self):
        """
        Installs the cross configuration file.
        """

        if self.authorized:
            logging.info("Starting installation of %s.", self.pyfunceble_destination)

            link = getattr(Infrastructure, f"links_{self.infrastructure_version}")[
                "config"
            ]["link"]

            logging.info(
                "Downloading %s into %s", repr(link), repr(self.pyfunceble_destination)
            )

            if not Download(link).text(self.pyfunceble_destination):
                raise CouldNotDownload(link)

            self.check_changes_and_commit(
                self.pyfunceble_destination,
                commit_message=Infrastructure.pyfunceble_config_update_message,
            )

            logging.info("Finished installation of %s.", self.pyfunceble_destination)

    def install_complementary_files(self):
        """
        Installs the complementary files.
        """

        for data in getattr(
            OurPyFuncebleConfig, f"links_{self.pyfunceble_version}"
        ).values():
            destination = f"{Outputs.current_directory}{data['destination']}"

            if not Download(data["link"]).text(destination):
                raise CouldNotDownload(data["link"])

    def start(self):
        logging.info(
            "Authorized to install %s: %s", self.pyfunceble_destination, self.authorized
        )

        self.install_config()
        self.install_complementary_files()
