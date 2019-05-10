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
from ultimate_hosts_blacklist.helpers import Command, Dict, Download, File
from ultimate_hosts_blacklist.input_repo_updater import logging
from ultimate_hosts_blacklist.input_repo_updater.configuration import Outputs
from ultimate_hosts_blacklist.input_repo_updater.configuration import (
    PyFunceble as InfrastructrePyFuncebleConfiguration,
)
from ultimate_hosts_blacklist.input_repo_updater.configuration import (
    directory_separator,
)


class OurPyFunceble:
    """
    Manage the way we work and interact with PyFunceble.
    """

    # Save the output directory.
    output_dir = "{0}output{1}".format(Outputs.current_directory, directory_separator)
    # Save the main instance of PyFunceble.
    pyfunceble = None
    # Save the InactiveDB submodule of PyFunceble.
    inactive_db = None
    # Save the Travis submodule of PyFunceble.
    travis = None

    def __init__(self):
        # We install PyFunceble.
        self.install()

        # We install the complementary files.
        self.download_complementary_files()

        # We merge older database entries into our new format.
        self.merge_inactive_database()

        # We import the inactive database and Travis class.
        from PyFunceble.inactive_db import InactiveDB
        from PyFunceble.auto_save import Travis

        # We initiate the inactive database.
        self.inactive_db = InactiveDB("api_call")
        # We initiate the Travis index.
        self.travis = Travis()

    @classmethod
    def __install_with_pip(cls, package, allow_stdout=False):
        """
        Install the given pip package.

        :param str package: The package to install.
        :param bool allow_stdout: Tell us if are allowed to directly write into stdout.
        """

        Command(
            "pip3 install --upgrade {0}".format(package), allow_stdout=allow_stdout
        ).execute()

    def install(self):
        """
        Install the right version of PyFunceble.
        """

        if InfrastructrePyFuncebleConfiguration.stable:
            # We are using the stable version of PyFunceble.

            logging.info("Installing production package of PyFunceble.")

            # We install the PyFunceble stable package.
            self.__install_with_pip(
                InfrastructrePyFuncebleConfiguration.packages["stable"],
                allow_stdout=True,
            )
        else:
            # We are using the development version of PyFunceble.

            logging.info("Installing development package of PyFunceble.")

            # We install the PyFunceble dev package.
            self.__install_with_pip(
                InfrastructrePyFuncebleConfiguration.packages["dev"], allow_stdout=True
            )

        # We import PyFunceble.
        import PyFunceble

        # We share it accros this class.
        self.pyfunceble = PyFunceble

        # and we load the configuration file.
        self.pyfunceble.load_config(
            generate_directory_structure=True,
            custom=InfrastructrePyFuncebleConfiguration.api_configuration,
        )

    @classmethod
    def download_complementary_files(cls):
        """
        Download all complementary files.
        """

        for _, data in InfrastructrePyFuncebleConfiguration.links.items():
            # We loop through the list of file to download.

            # We construct the destination of the file we are
            # going to download.
            file_path = "{0}{1}".format(Outputs.current_directory, data["destination"])

            if InfrastructrePyFuncebleConfiguration.stable:
                # We are using the stable version of PyFunceble.

                # We update the link to reflect that choice
                link = data["link"].replace("dev", "master")
            else:
                # We are using the dev version of PyFunceble.

                # We update the link to reflec that choice.
                link = data["link"].replace("master", "dev")

            if not Download(link, file_path).text():
                # We could not download the link.

                # We raise an exception, what if that file is important ?
                raise Exception("Unable to download {0}".format(repr(link)))

    def clean(self):
        """
        Clean all files we created from a previous session.
        """

        # We list the list of extra files to delete.
        files = [
            self.output_dir + Outputs.continue_filename,
            Outputs.current_directory + "dir_structure.json",
            Outputs.current_directory + "dir_structure_production.json",
        ]

        for file in files:
            # We loop through the list of directory.

            logging.info("Deletion of {0}".format(repr(file)))

            # We delete the currently read file path.
            File(file).delete()

        # We import PyFunceble.
        import PyFunceble

        # We load the configuration (locally as this will disappear along with
        # the exist of this method.)
        PyFunceble.load_config(generate_directory_structure=False)
        # And we run the PyFunceble cleaning tool.
        PyFunceble.Clean(None)

    def merge_inactive_database(self):
        """
        Merge the current state of the inactive database into
        the new format.
        """

        # We create an instance of the file.
        inactive_database_file = File(
            self.pyfunceble.CURRENT_DIRECTORY
            + self.pyfunceble.OUTPUTS["default_files"]["inactive_db"]
        )

        if inactive_database_file.exists():
            # The inactive file exists.

            logging.info(
                "Merging {0} into the new format.".format(
                    repr(inactive_database_file.file)
                )
            )

            # We get the content of the file.
            data = Dict.from_json(inactive_database_file.read())

            # We get the list of indexes to merge.
            to_merge = [index for index in data.keys() if index != "api_call"]

            if to_merge:
                # We have something to merge.

                for database in [data[index] for index in to_merge]:
                    # We loop through the database of the index
                    # to merge.

                    # We get its list of subjects to test.
                    database_subjects = [
                        y for index in database.values() for y in index
                    ]

                    if "api_call" in data:
                        # The api_call index exists.

                        if "to_test" in data["api_call"]:
                            # The to_test index exists under the api_call index.

                            # We extend it with the list of subject.
                            data["api_call"]["to_test"].extend(database_subjects)
                        else:
                            # The to_test index does not exists under the
                            # api_call index.

                            # We create it.
                            data["api_call"]["to_test"] = database_subjects

                for index in to_merge:
                    # We loop through the index to merge.

                    # And we delete them.
                    del data[index]

            logging.info(
                "Saving formated into {0}.".format(repr(inactive_database_file.file))
            )
            Dict(data).to_json(inactive_database_file.file)

    @classmethod
    def generate_percentage_file(cls, counters):
        """
        Print the percentage on file and screen.
        """

        from PyFunceble.percentage import Percentage

        Percentage(init=counters).log()

    def test(self, element, complete=False):
        """
        Given an element, we return the complete output of PyFunceble.
        """

        return self.pyfunceble.test(element, complete=complete)
