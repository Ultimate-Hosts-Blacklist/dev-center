"""
The tool to update the input repositories of the Ultimate-Hosts-Blacklist project.

Provides the PyFunceble updater. It updated everything which we need around
PyFunceble.

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

from ultimate_hosts_blacklist.helpers import Dict, Download, File

from ..config import Infrastructure, OurPyFuncebleConfig
from ..exceptions import CouldNotDownload
from .base import UpdaterBase


class PyFuncebleUpdater(UpdaterBase):
    """
    Provides the updater of the cross configuration file.
    """

    def authorization(self):
        return File(self.pyfunceble_cross_destination).exists()

    def start(self):
        logging.info(
            "Authorized to update %s: %s",
            self.pyfunceble_cross_destination,
            self.authorized,
        )

        logging.info("Starting update of %s.", self.pyfunceble_cross_destination)

        link = getattr(OurPyFuncebleConfig, f"links_{self.pyfunceble_version}")[
            "production_config"
        ]["link"]

        logging.info(
            "Downloading %s into %s",
            repr(link),
            repr(self.pyfunceble_cross_destination),
        )

        if not Download(link, self.pyfunceble_cross_destination).text():
            raise CouldNotDownload(link)

        cross_config = Dict.from_yaml(File(self.pyfunceble_cross_destination).read())
        cross_config = Dict(cross_config).merge(
            OurPyFuncebleConfig.configuration, strict=False
        )

        if "custom_pyfunceble_config" in self.administration:
            cross_config = Dict(cross_config).merge(
                self.administration.custom_pyfunceble_config, strict=False
            )

        logging.debug("Cross config file content:\n %s", cross_config)

        logging.info(
            "Writting latest PyFunceble configuration into %s",
            repr(self.pyfunceble_cross_destination),
        )
        Dict(cross_config).to_yaml(self.pyfunceble_cross_destination)
        logging.info(
            "Wrote latest PyFunceble configuration into %s",
            repr(self.pyfunceble_cross_destination),
        )

        logging.info(
            "Writting latest PyFunceble configuration into %s",
            repr(self.pyfunceble_destination),
        )
        Dict(cross_config).to_yaml(self.pyfunceble_destination)
        logging.info(
            "Wrote latest PyFunceble configuration into %s",
            repr(self.pyfunceble_destination),
        )

        self.check_changes_and_commit(
            self.pyfunceble_cross_destination,
            commit_message=Infrastructure.pyfunceble_config_update_message,
        )
        self.check_changes_and_commit(
            self.pyfunceble_destination,
            commit_message=Infrastructure.pyfunceble_config_update_message,
        )

        logging.info("Finished update of %s.", self.pyfunceble_cross_destination)
