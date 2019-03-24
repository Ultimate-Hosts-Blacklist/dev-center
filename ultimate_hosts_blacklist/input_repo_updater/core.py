"""
The tool to update the input repositories of the Ultimate-Hosts-Blacklist project.

Brain of the tool. Puts everything together.

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

from os import path, environ
from ultimate_hosts_blacklist.input_repo_updater import logging
from ultimate_hosts_blacklist.helpers import Dict, File
from ultimate_hosts_blacklist.input_repo_updater.configuration import (
    Infrastructure,
    Outputs,
)
from ultimate_hosts_blacklist.input_repo_updater.configuration import (
    PyFunceble as InfrastructrePyFuncebleConfiguration,
    Infrastructure,
)

from ultimate_hosts_blacklist.helpers import Regex, Command, Download, TravisCI
from time import time
from ultimate_hosts_blacklist.input_repo_updater.administration import Administration
from ultimate_hosts_blacklist.input_repo_updater.authorization import Authorization


class Core:
    """
    Brain of the tool.
    """

    def __init__(self, logging_level=logging.INFO):
        logging.basicConfig(
            format="%(asctime)s - %(levelname)s -- %(message)s", level=logging_level
        )

        TravisCI.configure_git_repo()
        TravisCI.fix_permissions()

        self.administation = Administration()
        self.information = self.administation.data

        self.authorization = Authorization(self.information)

        self.update_cross_pyfunceble_configuration_file()
        self.install_cross_pyfunceble_configuration_file()

    def update_cross_pyfunceble_configuration_file(self):
        """
        Install the cross repository configuration which is shared with
        all input sources.
        """

        destination = "{0}{1}".format(
            Outputs.current_directory,
            Infrastructure.links["config"]["cross_destination"],
        )
        config_destination = "{0}{1}".format(
            Outputs.current_directory, Infrastructure.links["config"]["destination"]
        )

        if path.isfile(destination):
            logging.info(
                "Cross configuration file ({0}) found. Starting updating process.".format(
                    destination
                )
            )

            if InfrastructrePyFuncebleConfiguration.stable:
                link = InfrastructrePyFuncebleConfiguration.links["production_config"][
                    "link"
                ]
            else:
                link = InfrastructrePyFuncebleConfiguration.links["production_config"][
                    "link"
                ]

            logging.info(
                "Downloading {0} into {1}".format(repr(link), repr(destination))
            )

            if not Download(link, destination).link():
                raise Exception("Unable to download {0}.".format(repr(link)))

            try:
                _ = environ["TRAVIS_BUILD_DIR"]
                travis_branch = environ["GIT_BRANCH"]
            except KeyError:
                travis_branch = "master"

            regex_match = r"({0}\:)(.*)"

            content = File(destination).read()

            for (
                index,
                value,
            ) in InfrastructrePyFuncebleConfiguration.configuration.items():
                content = Regex(content, regex_match.format(index)).replace_with(
                    "\1 {0}".format(value)
                )

            content = Regex(content, regex_match.format("travis_branch")).replace_with(
                "\1 {0}".format(travis_branch)
            )

            logging.debug("Cross configuration file: \n {0}".format(content))

            logging.info(
                "Writting latest configuration into {0}".format(repr(destination))
            )
            File(destination).write(content, overwrite=True)

            logging.info(
                "Writting latest configuration into {0}".format(
                    repr(config_destination)
                )
            )
            File(config_destination).write(content, overwrite=True)
        else:
            logging.info(
                "Cross configuration file ({0}) not found.".format(destination)
            )

    def install_cross_pyfunceble_configuration_file(self):
        """
        Install the cross repository configuration which is shared with
        all input sources.
        """

        destination = "{0}{1}".format(
            Outputs.current_directory, Infrastructure.links["config"]["destination"]
        )

        if not path.isfile(
            "{0}{1}".format(
                Outputs.current_directory,
                Infrastructure.links["config"]["cross_destination"],
            )
        ):
            logging.info(
                "Installing the cross repository file into {0}".format(
                    repr(destination)
                )
            )
            if not Download(
                InfrastructrePyFuncebleConfiguration.links["production_config"]["link"],
                destination,
            ).link():
                raise Exception(
                    "Unable to download {0}.".format(
                        repr(
                            InfrastructrePyFuncebleConfiguration.links[
                                "production_config"
                            ]["link"]
                        )
                    )
                )
        else:
            logging.info("Cross repository file not installed. Already present.")

    def process(self):
        """
        Processes the whole logic.
        """

        a = 0
