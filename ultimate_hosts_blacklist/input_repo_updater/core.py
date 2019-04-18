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
# pylint: disable=bad-continuation
from itertools import chain
from multiprocessing import Manager, Process
from os import environ, path
from time import time

from ultimate_hosts_blacklist.helpers import Dict, Download, File, List, Regex, TravisCI
from ultimate_hosts_blacklist.input_repo_updater import Fore, Style, logging
from ultimate_hosts_blacklist.input_repo_updater.administration import Administration
from ultimate_hosts_blacklist.input_repo_updater.authorization import Authorization
from ultimate_hosts_blacklist.input_repo_updater.configuration import (
    Infrastructure,
    Outputs,
)
from ultimate_hosts_blacklist.input_repo_updater.configuration import (
    PyFunceble as InfrastructrePyFuncebleConfiguration,
)
from ultimate_hosts_blacklist.input_repo_updater.our_pyfunceble import OurPyFunceble
from ultimate_hosts_blacklist.whitelist import clean_list_with_official_whitelist


class Core:  # pylint: disable=too-many-instance-attributes
    """
    Brain of the tool.

    :param bool multiprocessing: Activate/Deactivate the multiple process usage.

    :param int logging_level: Set the logging level.
    """

    def __init__(self, multiprocessing=False, logging_level=logging.INFO):
        # We configurate the logging.
        logging.basicConfig(
            format="%(asctime)s - %(levelname)s -- %(message)s", level=logging_level
        )

        # We share the multiprocessing.
        self.multiprocessing = multiprocessing

        # We configurate the repository.
        TravisCI.configure_git_repo()
        # We fix the permissions of the repository.
        TravisCI.fix_permissions()

        # We initiate our administration logic.
        self.administation = Administration()
        # We get our administration data.
        self.information = self.administation.data

        # We get the global authorization.
        #
        # Note: If we are authorized to operate this class
        # also initiate/downlaod the data we are going to test.
        self.authorization = Authorization(self.information)

        # We starts a File instance with the continue file.
        # The objective of the continue file is to allow
        # us to continue between processes.
        self.continue_file = File(Outputs.continue_destination)

        # Same for the temp volatile file.
        self.temp_volatile_file = File(Outputs.temp_volatile_destination)
        # Same for the official volatile file.
        self.volatile_file = File(Outputs.volatile_destination)
        # Same for the official clean file.
        self.clean_file = File(Outputs.clean_destination)
        # Same fot the official whitelisted file.
        self.whitelisted_file = File(Outputs.whitelisted_destination)

        if self.authorization.authorized:
            # We are authorized to launch the testing logic.

            # We update the cross repository file.
            self.update_cross_pyfunceble_configuration_file()
            # We install the repository file.
            self.install_cross_pyfunceble_configuration_file()

            # We initiate PyFunceble
            self.our_pyfunceble = OurPyFunceble()

            if self.authorization.clean:
                # We are authorized to clean.

                # We process the cleaning of the output directory.
                self.our_pyfunceble.clean()

    @classmethod
    def update_cross_pyfunceble_configuration_file(cls):
        """
        Install the cross repository configuration which is shared with
        all input sources.
        """

        # We construct the path to the file we are going to write.
        destination = "{0}{1}".format(
            Outputs.current_directory,
            Infrastructure.links["config"]["cross_destination"],
        )

        # We construct the path to the file which is loaded by PyFunceble.
        config_destination = "{0}{1}".format(
            Outputs.current_directory, Infrastructure.links["config"]["destination"]
        )

        if path.isfile(destination):
            # The cross repository file exists.

            logging.info(
                "Cross configuration file ({0}) found. Starting updating process.".format(
                    destination
                )
            )

            if InfrastructrePyFuncebleConfiguration.stable:
                # We are working with the stable version
                # of PyFunceble.

                # We get the stable link to the configuration file.
                link = InfrastructrePyFuncebleConfiguration.links["production_config"][
                    "link"
                ].replace("dev", "master")
            else:
                # We are working with the development version
                # of PyFunceble.

                # We get the dev link to the configuration file..
                link = InfrastructrePyFuncebleConfiguration.links["production_config"][
                    "link"
                ].replace("master", "dev")

            logging.info(
                "Downloading {0} into {1}".format(repr(link), repr(destination))
            )

            if not Download(link, destination).link():
                # We could not download the configuration file.

                # We raise an exception, we can't continue without a configuration
                # file.
                raise Exception("Unable to download {0}.".format(repr(link)))

            try:
                # We are under Travis CI.
                _ = environ["TRAVIS_BUILD_DIR"]

                # We extract the branch we are working with
                # from the GIT_BRANCH environment variable.
                travis_branch = environ["GIT_BRANCH"]
            except KeyError:
                # We are not under Travis CI.

                # We set the branch as master.
                travis_branch = "master"

            # We set the regex which will match a line from
            # the PyFunceble configuration.
            regex_match_configuration_line = r"({0}\:)(.*)"

            # We get the content of the cross configuration file.
            content = File(destination).read()

            for (
                index,
                value,
            ) in InfrastructrePyFuncebleConfiguration.configuration.items():
                # We loop though the configuration items.

                if isinstance(value, str):
                    # The value is a string.

                    # We get its representation.
                    value = repr(value)

                # We update the content with the new value.
                content = Regex(
                    content, regex_match_configuration_line.format(index)
                ).replace_with(r"\1 {0}".format(value))

            # We set the travis branch.
            content = Regex(
                content, regex_match_configuration_line.format("travis_branch")
            ).replace_with(r"\1 {0}".format(travis_branch))

            logging.debug("Cross configuration file content: \n {0}".format(content))

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

    @classmethod
    def install_cross_pyfunceble_configuration_file(cls):
        """
        Install the cross repository configuration which is shared with
        all input sources.
        """

        # We construct the path to the configuration file.
        destination = "{0}{1}".format(
            Outputs.current_directory, Infrastructure.links["config"]["destination"]
        )

        if not path.isfile(
            "{0}{1}".format(
                Outputs.current_directory,
                Infrastructure.links["config"]["cross_destination"],
            )
        ):
            # The cross configuration file do not exists.

            logging.info(
                "Installing the cross repository file into {0}".format(
                    repr(destination)
                )
            )

            if not Download(
                InfrastructrePyFuncebleConfiguration.links["production_config"]["link"],
                destination,
            ).link():
                # We could not download the cross configuration file.

                # We raise an exception, we can't work without a configuration file.
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
            logging.info("Cross repository file not installed: Already present.")

    def __is_in_continue_data(self, subject, continue_data=None):
        """
        Given a subject and a continue data, we check if subject present into
        continue data.

        :param str subject: The subject we are working with.
        :param dict continue_data:
            The content of the continue data.

            .. note::
                If this is not given or set to a :code:`NoneType`, we load the file.

        :return: The presence.
        :rtype: bool
        """

        if not continue_data:
            # The continue data is not given.

            # We get it from the file.
            continue_data = Dict.from_json(self.continue_file.read())

        for status in continue_data:
            # We loop through the list of status.

            if subject in continue_data[status]:
                # The status is in the currently read
                # status index.

                # We return True, it is present.
                return True

        # We return False, it is not present.
        return False

    def test(self, subject, continue_data=None, manager_continue_data=None):
        """
        Do the test and more.

        :param str subject: The subject we are testing.
        :param dict continue_data:
            The content of the continue data.

            .. note::
                If this is not given or set to a :code:`NoneType`, we load the file.

        :param multiprocessing.Manager.list manager_continue_data:
            A manager process which will let us save the state of the continue
            data once the test finished.
        """

        if not continue_data and manager_continue_data is None:
            # * The continue data is not given
            # and
            # * No manager data is given.

            # We get the continue data from its file.
            continue_data = Dict.from_json(self.continue_file.read())
        else:
            continue_data = {}

        # We test and get the result of the test.
        test_result = self.our_pyfunceble.test(subject, complete=True)

        # We get the status.
        status = test_result["status"]

        if test_result["_status"] != "ACTIVE" and status == "ACTIVE":
            # The special rule was applied.

            # We save the current subject into the volatile file.
            self.temp_volatile_file.write("{0}\n".format(subject), overwrite=False)

        if status == "ACTIVE":
            # The status is ACTIVE.

            # We set the coloration to green.
            coloration = Fore.GREEN + Style.BRIGHT
        elif status == "INACTIVE":
            # The status is INACTIVE.

            # We set the coloration to red.
            coloration = Fore.RED + Style.BRIGHT
        else:
            # The status is INVALID.

            # We set hte coloration to cyan.
            coloration = Fore.CYAN + Style.BRIGHT

        # We print the status on screen.
        print("{0} is {1}".format(coloration + repr(subject), status))

        if status in continue_data:
            # The status is in the continue data.

            # We append the current subject into its index.
            continue_data[status].append(subject)
        else:
            # The status is not in the continue data.

            # We create the its index.
            continue_data[status] = [subject]

        if manager_continue_data is not None:
            # The manager is given,

            # We append the current state of the continue_data.
            manager_continue_data.append(continue_data)
        else:
            # The manager is not given.

            # We save the current state of the continue data
            # into its file.
            Dict(continue_data).to_json(Outputs.continue_destination)

    def __process_simple(self, to_test, end_time):
        """
        Process a single process test.

        :param itertools to_test: The list to test in a :code:`chain`.
        :param int end_time: The end time of the current process.
        """

        while int(time()) < end_time:
            # We loop untill the end time is in the past.

            try:
                # We get the subject we are going to test.
                subject = next(to_test).strip()

                if not subject:
                    # The subject is empty or equal to None.

                    # We continue the loop.
                    continue

                if self.__is_in_continue_data(subject):
                    # The subject is in the continue data.

                    # We continue the loop.
                    continue

                # We process the test and everything related to
                # it.
                self.test(subject)
            except StopIteration:
                # No subjects is available. We finished to test
                # everything.

                # We set that we are not under test anymore.
                #
                # Note: Not under test means that we finished to
                # test the `domains.list` file completly.
                self.information["currently_under_test"] = False

                # We break the loop.
                break

        # We save the administration data.
        self.administation.save()

    def __process_multiprocess(self, to_test, end_time):
        """
        Process a single process test.

        :param itertools to_test: The list to test in a :code:`chain`.
        :param int end_time: The end time of the current process.
        """

        # We create a list which will save the list of
        # all currently running processes.
        processes = []

        with Manager() as manager:
            # We process with the manager.

            # We initiate a manager list.
            manager_list = manager.list([])

            while int(time()) < end_time:
                # We loop untill the end time is in the past.

                try:
                    # We get the subject we are going to test.
                    subject = next(to_test).strip()

                    if not subject:
                        # The subject is empty or equal to None.

                        # We continue the loop.
                        continue

                    # We initiate a process which will test the current domain.
                    process = Process(
                        target=self.test, args=(subject, None, manager_list)
                    )
                    # We append the process into the "pool" of processes.
                    processes.append(process)

                    # We start the process.
                    process.start()

                    # And we continue the loop.
                    continue
                except StopIteration:
                    # No subjects is available. We finished to test
                    # everything.

                    # We set that we are not under test anymore.
                    #
                    # Note: Not under test means that we finished to
                    # test the `domains.list` file completly.
                    self.information["currently_under_test"] = False

                    # We break the loop.
                    break

            for process in processes:
                # We loop through the list of processes.

                # And we block until the currently read
                # process finished.
                process.join()

            # We initiate the future content of the
            # continue data file.
            continue_data = {}

            for data in manager_list:
                # We loop through the list of manager entries.

                for indexes in data:
                    # We loop through the indexes of the
                    # currently read data.

                    if indexes in continue_data:
                        # The currently read index is already into the
                        # continue data.

                        # We extend its index into the continue data
                        # with the index saved in the manager.
                        continue_data[indexes].extend(data[indexes])
                    else:
                        # The currently read index is not into the
                        # continue data.

                        # We create its index into the continue data
                        # with the saved (and currently read) data
                        continue_data[indexes] = data[indexes]

                    # We remove all duplicates from the read/set index.
                    continue_data[indexes] = List(continue_data[indexes]).format()

                    if indexes != "ACTIVE":
                        # The index is not ACTIVE.

                        for subject in data[indexes]:
                            # We loop through the list of member of the currently
                            # read index.

                            # We add each members of the index
                            # data into the inactive database.
                            self.our_pyfunceble.inactive_db.add(subject)

            # We save the continue data into its file.
            Dict(continue_data).to_json(self.continue_file.file)

        # We save the administration file.
        self.administation.save()

    def end_management(self):
        """
        Manage what we do once all processes are stopped.
        """

        if self.our_pyfunceble.travis.authorized:
            # We are authorized to commit/push.

            if self.information["currently_under_test"]:
                # We are still currently under test.

                logging.info("Still some data to test.")
                logging.info("Launching auto continue commit/push and exit.")

                # We save and move to the next sequence.
                self.our_pyfunceble.travis.not_end_commit()
            else:
                # There is nothing to test anymore.

                logging.info("Test finished.")
                logging.info("Launching auto save commit/push and exit.")

                # We save.
                self.our_pyfunceble.travis.end_commit()

    def set_percentage(self):
        """
        Create the percentage file.
        """

        # We get the content of the continue data.
        continue_data = Dict.from_json(self.continue_file.read())

        # We map the local status with what PyFunceble understand for the
        # percentage.
        status_map = {"ACTIVE": "up", "INACTIVE": "down", "INVALID": "invalid"}

        # We initiate the counters for the status we have locally.
        counters = {status_map[x]: len(y) for x, y in continue_data.items()}

        # We  complete with the status which are not found locally.
        counters.update({x: 0 for x in status_map.values() if x not in counters})
        # We set the number of tested.
        counters["tested"] = sum(counters.values())

        logging.info(counters)

        # We ask PyFunceble to generate the percentage file.
        self.our_pyfunceble.generate_percentage_file(counters)

    def update_clean_list(self):
        """
        Update the content of the clean list.
        """

        logging.info("Started the generation of {0}".format(repr(self.clean_file.file)))

        # We get the path to the file we are going to read.
        input_file = File(Outputs.active_subjects_destination)

        if input_file.exists():
            # The input file exists.

            # We get its content into list format.
            clean_list = input_file.to_list()

            # We remove every uneeded lines.
            clean_list = Regex(clean_list, "^#").not_matching_list()

            # We remove any duplicates.
            clean_list = List(clean_list).format(delete_empty=True)

            # We finaly save everything into the destination.
            self.clean_file.write("\n".join(clean_list), overwrite=True)

        logging.info(
            "Finished the generation of {0}".format(repr(self.clean_file.file))
        )

    def update_whitelisted_list(self):
        """
        Update the content of the whitelisted list.
        """

        logging.info(
            "Started the generation of {0}".format(repr(self.whitelisted_file.file))
        )

        if self.clean_file.exists():
            # The input file exists.

            # We get its content into list format.
            clean_list = self.clean_file.to_list()

            # We whitelist its content.
            whitelisted_list = clean_list_with_official_whitelist(
                clean_list, multiprocessing=True, processes=60
            )

            # We remove any duplicated.
            whitelisted_list = List(whitelisted_list).format(delete_empty=True)

            # We finaly save everything into the destination.
            self.whitelisted_file.write("\n".join(whitelisted_list), overwrite=True)

        logging.info(
            "Finished the generation of {0}".format(repr(self.whitelisted_file.file))
        )

    def update_volatile_list(self):
        """
        Update the content of the volatile list.
        """

        logging.info(
            "Started the generation of {0}".format(repr(self.volatile_file.file))
        )

        volatile_list = []

        if self.temp_volatile_file.exists():
            # The input file exists.

            # We get its content into list format.
            volatile_list.extend(self.temp_volatile_file.to_list())

        # We append the content of the previously whitelisted list.
        volatile_list.extend(self.whitelisted_file.to_list())

        # We whitelist the finale content content.
        volatile_list = clean_list_with_official_whitelist(
            volatile_list, multiprocessing=True, processes=60
        )

        # We remove any duplicated.
        volatile_list = List(volatile_list).format(delete_empty=True)

        # We finaly save everything into the destination.
        self.volatile_file.write("\n".join(volatile_list), overwrite=True)

        logging.info(
            "Finished the generation of {0}".format(repr(self.volatile_file.file))
        )

    def process(self):
        """
        Processes the whole logic.
        """

        # We get the current time as start time.
        start_time = int(time())
        # We calculate the end time in second.
        end_time = start_time + (
            InfrastructrePyFuncebleConfiguration.configuration[
                "travis_autosave_minutes"
            ]
            * 60
        )

        # We get the list to test.
        to_test = File(Outputs.input_destination).to_list()

        if not self.continue_file.exists():
            # The continue file do not exists.

            # We create it.
            Dict({}).to_json(self.continue_file.file)

        # We get the content of the continue file.
        continue_data = Dict.from_json(self.continue_file.read())

        # pylint: disable=consider-using-set-comprehension

        # We construct the list to test.
        #
        # Components:
        #   * List to test (- minus ) Already saved into the
        #   inactive data (last tested at most 1 day ago).
        #   * The inactive data to rested (last tested at least 1 day ago)
        to_test = chain(
            list(
                set([x for x in to_test if x not in self.our_pyfunceble.inactive_db])
                - set([y for x in continue_data.values() for y in x])
            ),
            self.our_pyfunceble.inactive_db["to_test"],
        )

        if not self.information["currently_under_test"]:
            # We are not currently under test.

            # We set that we now are under test.
            self.information["currently_under_test"] = True

            # We save the administration data..
            self.administation.save()

        # We delete everything which is not needed from the memory.
        del continue_data, start_time

        if not self.multiprocessing:
            # We are not authorized to use multiple process.

            # We run a single process test.
            self.__process_simple(to_test, end_time)
        else:
            # We are authorized to use multiple process.

            # We run a multiprocess test.
            self.__process_multiprocess(to_test, end_time)

        logging.info("Test processes stopped.")

        # We set/create the percentage file.
        self.set_percentage()

        # We update/create the clean list.
        self.update_clean_list()

        # We update/create the whitelisted list.
        self.update_whitelisted_list()

        # We udpdate/create the whitelisted list.
        self.update_volatile_list()

        # And we manage the end of the tool.
        self.end_management()