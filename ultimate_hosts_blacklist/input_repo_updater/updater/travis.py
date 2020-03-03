"""
The tool to update the input repositories of the Ultimate-Hosts-Blacklist project.

The Travis Updater. It provides the updater of the Travis CI configuration.


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

from PyFunceble.helpers import Download, EnvironmentVariable, File

from ultimate_hosts_blacklist.helpers import Dict

from ..config import Infrastructure, Outputs
from .base import UpdaterBase


class TravisUpdater(UpdaterBase):
    """
    Provides the Travis Configuration file updater.
    """

    # Tell us which index we have to delete.
    to_delete = ["addons", "cache", "matrix", "python", "sudo"]
    # Tell us which index we have to update.
    to_update = ["dist", "install", "language", "notifications", "script"]

    def authorization(self):
        return not File(Outputs.central_destination).exists()

    @classmethod
    def get_local_version(cls):
        """
        Provides the local version of the configuration file.
        """

        if (
            EnvironmentVariable("GIT_BRANCH").exists()
            and EnvironmentVariable("TRAVIS_BUILD_DIR").exists()
        ):
            logging.info("Reading local version of %s", repr(Outputs.travis_filename))
            content = File(Outputs.travis_destination).read()
            logging.debug("Local Content:\n%s", content)

            return Dict.from_yaml(content)

        return dict()

    def get_central_vesion(self):
        """
        Provides the central version of the configuration file.
        """

        if (
            EnvironmentVariable("GIT_BRANCH").exists()
            and EnvironmentVariable("TRAVIS_BUILD_DIR").exists()
        ):
            logging.info("Getting central version of %s", repr(Outputs.travis_filename))

            if (
                "infrastructure_version" in self.administration
                and Infrastructure.is_version_known(
                    self.administration.pyfunceble_version
                )
            ):
                link = getattr(
                    Infrastructure,
                    f"links_{self.administration.infrastructure_version}",
                )["travis_config"]["link"]
            else:
                link = getattr(
                    Infrastructure, f"links_{Infrastructure.default_version}"
                )["travis_config"]["link"]

            upstream = Download(link).text()

            if isinstance(upstream, str):
                content = Dict.from_yaml(upstream)
                logging.debug("Upstream Content:\n%s", content)

                return content
        return dict()

    def merge(self, local, central):
        """
        Merges the upstream into the local version.
        """

        if (
            EnvironmentVariable("GIT_BRANCH").exists()
            and EnvironmentVariable("TRAVIS_BUILD_DIR").exists()
        ):
            for index in self.to_update:
                if index in central:
                    local[index] = central[index]
                    logging.info(
                        "Merging %s into %s", repr(index), repr(Outputs.travis_filename)
                    )
                else:
                    del local[index]
                    logging.info(
                        "Deleted %s because not present in central.", repr(index)
                    )

            flattened = Dict(local).flatten()

            for index in self.to_delete:
                logging.info("Merging %s into %s", index, repr(Outputs.travis_filename))

                if index in flattened:
                    del flattened[index]
                    logging.info("Deleted %s as it is not desired.", repr(index))

            return Dict(flattened).unflatten()

        return dict()

    @classmethod
    def save(cls, data):
        """
        Saves the given data at the final location.
        """

        if (
            EnvironmentVariable("GIT_BRANCH").exists()
            and EnvironmentVariable("TRAVIS_BUILD_DIR").exists()
        ):

            logging.info("Saving new version into %s", repr(Outputs.travis_filename))
            Dict(data).to_yaml(Outputs.travis_destination)
            logging.info("Saved new version into %s", repr(Outputs.travis_filename))

    def start(self):
        local_version = self.get_local_version()
        central_version = self.get_central_vesion()

        if local_version and central_version:
            merged = self.merge(local_version, central_version)

            logging.debug("Merged version of %s:\n%s", Outputs.travis_filename, merged)

            self.save(merged)

            self.check_changes_and_commit(
                Outputs.travis_destination,
                commit_message=Infrastructure.travis_config_update_message,
            )
