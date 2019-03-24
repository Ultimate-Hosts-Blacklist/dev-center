"""
The tool to update the input repositories of the Ultimate-Hosts-Blacklist project.

Provide the way we interact with PyFunceble.

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
import pip
from ultimate_hosts_blacklist.input_repo_updater import logging
from ultimate_hosts_blacklist.input_repo_updater.configuration import (
    PyFunceble as InfrastructrePyFuncebleConfiguration,
)
from ultimate_hosts_blacklist.input_repo_updater.configuration import (
    Outputs,
    directory_separator,
)
from ultimate_hosts_blacklist.helpers import Download, File


class PyFunceble:
    """
    Manage the way we work and interact with PyFunceble.
    """

    def __install_from_pip(self, package):
        """
        Install the given pip package.
        """

        if hasattr(pip, "main"):
            pip.main(["install", package])
        else:
            pip._internal.main(["install", package])

    def install(self):
        """
        Install the right version of PyFunceble.
        """

        if InfrastructrePyFuncebleConfiguration.stable:
            logging.info("Installing PyFunceble.")
            self.__install_from_pip("PyFunceble")
        else:
            self.__install_from_pip("PyFunceble-dev")

    def delete_deprecated_files(self):
        """
        Delete old deprecated files of our infrastructure and PyFunceble.
        """

        files = ["tool.py", "PyFunceble.py", "requirements.txt"]

        for file in files:
            File("{0}{1}".format(Outputs.current_directory, file)).delete()

    def download_complementary_files(self):
        """
        Download all complementary files.
        """

        for data in InfrastructrePyFuncebleConfiguration.links:
            file_path = "{0}{1}".format(Outputs.current_directory, data["destination"])

            if InfrastructrePyFuncebleConfiguration.stable:
                link = data["link"].replace("dev", "master")
            else:
                link = data["link"].replace("master", "dev")

            if not Download(link, file_path).link():
                raise Exception("Unable to download {0}".format(repr(link)))

        self.delete_deprecated_files()

    @classmethod
    def clean(cls):
        """
        Clean all files we created from a previous session.
        """

        files = []

        for file in files:
            File(
                "{0}output{1}{2}".format(
                    Outputs.current_directory, directory_separator, file
                )
            ).delete()

