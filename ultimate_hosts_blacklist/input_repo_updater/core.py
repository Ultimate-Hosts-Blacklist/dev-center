"""
The tool to update the input repositories of the Ultimate-Hosts-Blacklist project.

Brain of the tool. Puts everything together.

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
# pylint: disable=bad-continuation

import sys
from datetime import datetime
from itertools import chain, repeat
from multiprocessing import Manager, Pool, active_children
from os import cpu_count, environ, path
from shutil import move, rmtree

from domain2idna import get as domain2idna

import ultimate_hosts_blacklist.input_repo_updater as launcher
from ultimate_hosts_blacklist.helpers import Dict, Download, File, List, Regex
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
from ultimate_hosts_blacklist.input_repo_updater.travis_config import TravisConfig
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
        self.processes = cpu_count()

        # We initiate our administration logic.
        self.administation = Administration()
        # We get our administration data.
        self.information = self.administation.data

        # We initiate PyFunceble
        self.our_pyfunceble = OurPyFunceble()

        # We update the travis configuration file if needed.
        TravisConfig()

        # We update the cross repository file.
        self.update_cross_pyfunceble_configuration_file()

        # We install the repository file.
        self.install_cross_pyfunceble_configuration_file()

        # We get the global authorization.
        #
        # Note: If we are authorized to operate this class
        # also initiate/downlaod the data we are going to test.
        self.authorization = Authorization(
            self.information, shared_pyfunceble=self.our_pyfunceble
        )

        # We starts a File instance with the continue file.
        # The objective of the continue file is to allow
        # us to continue between processes.
        self.continue_file = File(Outputs.continue_destination)

        # Same for the temp volatile file.
        self.temp_volatile_file = File(Outputs.temp_volatile_destination)
        # Same for the official volatile file.
        self.volatile_file = File(Outputs.volatile_destination)
        # Same for the official ip file.
        self.ip_file = File(Outputs.ip_destination)
        # Same for the official clean file.
        self.clean_file = File(Outputs.clean_destination)
        # Same fot the official whitelisted file.
        self.whitelisted_file = File(Outputs.whitelisted_destination)

        if self.authorization.authorized:
            # We are authorized to launch the testing logic.

            if self.authorization.clean:
                # We are authorized to clean.

                # We process the cleaning of the output directory.
                self.our_pyfunceble.clean()

            logging.info("Launcher version: {0}".format(launcher.VERSION))
            logging.info(
                "PyFunceble version: {0}".format(self.our_pyfunceble.pyfunceble.VERSION)
            )

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

            if not Download(link, destination).text():
                # We could not download the configuration file.

                # We raise an exception, we can't continue without a configuration
                # file.
                raise Exception("Unable to download {0}.".format(repr(link)))

            try:
                # We are under Travis CI.
                _ = environ["TRAVIS_BUILD_DIR"]

                # We extract the branch we are working with
                # from the GIT_BRANCH environment variable.
                ci_branch = environ["GIT_BRANCH"]
            except KeyError:
                # We are not under Travis CI.

                # We set the branch as master.
                ci_branch = "master"

            # We get the content of the PyFunceble production configuration file.
            cross_config = Dict.from_yaml(File(destination).read())
            cross_config = Dict(cross_config).merge(
                InfrastructrePyFuncebleConfiguration.configuration, strict=False
            )

            # We set the travis branch.
            cross_config["ci_branch"] = ci_branch

            logging.debug(
                "Cross configuration file content: \n {0}".format(cross_config)
            )

            logging.info(
                "Writting latest configuration into {0}".format(repr(destination))
            )
            Dict(cross_config).to_yaml(destination)

            logging.info(
                "Writting latest configuration into {0}".format(
                    repr(config_destination)
                )
            )
            Dict(cross_config).to_yaml(config_destination)

            TravisConfig.check_changes_and_commit(
                destination,
                commit_message=Infrastructure.pyfunceble_config_update_message,
            )
            TravisConfig.check_changes_and_commit(
                config_destination,
                commit_message=Infrastructure.pyfunceble_config_update_message,
            )
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

            if Infrastructure.stable:
                link = Infrastructure.links["config"]["link"].replace("dev", "master")
            else:
                link = Infrastructure.links["config"]["link"].replace("master", "dev")

            if not Download(link, destination).text():
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

            TravisConfig.check_changes_and_commit(
                destination,
                commit_message=Infrastructure.pyfunceble_config_update_message,
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

        for subjects in continue_data.values():
            # We loop through the list of status.

            if subject in subjects:
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
        # We get the source.
        source = test_result["status_source"]
        # We get the HTTP status code.
        status_code = test_result["http_status_code"]

        if test_result["_status"] != status or test_result["_status_source"] != source:
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
        print(
            "{0} is {1} ({2} - {3})".format(
                coloration + repr(subject), status, source, status_code
            )
        )

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

    @classmethod
    def _extract_domains_from_line(cls, line, converter):
        """
        Given a line, we return the domains.

        :param str line: The line to format.

        :return: The partially formatted line.
        :rtype: str, list
        """

        return converter(line).get_converted()

    def __get_subject_to_test(self, subject):
        """
        Given the subject (line), we format
        and return a list of subject to test next.
        """

        result = []

        if subject and not subject.startswith("#"):
            # The subject is empty or equal to None.

            # We extract the subject from the given line.
            pre_result = domain2idna(subject)

            if pre_result.startswith("www."):
                # The subject starts with "www."

                # We create a list of subject to test.
                result.extend([pre_result, pre_result[4:]])
            elif self.our_pyfunceble.pyfunceble.is_domain(
                pre_result
            ) and not self.our_pyfunceble.pyfunceble.is_subdomain(pre_result):
                # * The line is a domain.
                # and
                # * The line is not a subdomain.

                # We create a list of subject to test.
                result.extend([pre_result, "www.{0}".format(pre_result)])
            else:
                result.append(pre_result)

        for index, res in enumerate(result):
            if self.__is_in_continue_data(res):
                del result[index]

        return result

    def __process_simple(self, to_test, end_time):
        """
        Process a single process test.

        :param itertools to_test: The list to test in a :code:`chain`.
        :param int end_time: The end time of the current process.
        """

        while int(datetime.now().timestamp()) < end_time:
            # We loop untill the end time is in the past.

            try:
                # We get the subject we are going to test.
                subject = next(to_test).strip()

                for subject in self.__get_subject_to_test(subject):
                    # We loop through the list of subject to test.

                    # We process the test and everything related to
                    # it.
                    self.test(subject)

                # And we continue the loop
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

        # We save the administration data.
        self.administation.save()

    @classmethod
    def __check_exception(cls, processes):
        """
        Check if an exception is present into the given pool of processes.

        :param list processes. A list of running processes.
        """

        exception_present = False
        traceback = None

        for process in processes:
            # We loop through the list of processes.

            if exception_present:
                # We kill the process.
                process.terminate()
                continue

            try:
                if process.exception and not exception_present:
                    # There in an exception in the currently
                    # read process.

                    # We get the traceback
                    _, traceback = process.exception

                    # We print the traceback.
                    print(traceback)
                    logging.error(traceback)

                    exception_present = True
            except (AttributeError, OSError):
                continue

        if exception_present:
            print(traceback)
            sys.exit(1)

    def __process_multiprocess(self, to_test, end_time):
        """
        Process a single process test.

        :param itertools to_test: The list to test in a :code:`chain`.
        :param int end_time: The end time of the current process.
        """

        with Manager() as manager:
            # We process with the manager.

            # We initiate a manager list.
            manager_list = manager.list()

            while True:
                # We loop untill the end time is in the past.

                logging.debug("ACTIVE Children: {0}".format(active_children()))
                logging.debug(
                    "WHILE_STATE: {0}".format(
                        len(active_children()) <= self.processes
                        and int(datetime.now().timestamp()) < int(end_time)
                    )
                )

                while len(active_children()) <= self.processes and int(
                    datetime.now().timestamp()
                ) < int(end_time):

                    try:
                        # We get the subject we are going to test.
                        subject = next(to_test).strip()

                        for subject in self.__get_subject_to_test(subject):
                            # We loop through the list of subject to test.

                            # We initiate a process which will test the current domain.
                            process = self.our_pyfunceble.pyfunceble.core.multiprocess.OurProcessWrapper(
                                target=self.test, args=(subject, None, manager_list)
                            )

                            process.name = f"Ultimate {subject}"
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

                self.__check_exception(active_children())

                while (
                    len(active_children()) >= self.processes
                    and "ultimate"
                    in " ".join([x.name for x in reversed(active_children())]).lower()
                ):
                    logging.debug(
                        "Still active: {0}".format(
                            [x.name for x in reversed(active_children())]
                        )
                    )

                if (
                    not self.information["currently_under_test"]
                    or int(datetime.now().timestamp()) > end_time
                ):

                    while (
                        "ultimate"
                        in " ".join(
                            [x.name for x in reversed(active_children())]
                        ).lower()
                    ):
                        continue

                    # We initiate the future content of the
                    # continue data file.
                    continue_data = Dict.from_json(self.continue_file.read())

                    for data in manager_list:
                        # We loop through the list of manager entries.

                        logging.info("Merging processes data.")

                        # We merge the currently read data with the continue file.
                        continue_data = Dict(continue_data).merge(data, strict=False)

                    # We save the continue data into its file.
                    Dict(continue_data).to_json(self.continue_file.file)

                    break

        current_time = datetime.now()

        if not self.information["currently_under_test"]:
            self.information["end_epoch"] = current_time.timestamp()
            self.information["end_datetime"] = current_time.strftime("%c")
        else:
            self.information["last_autosave_epoch"] = current_time.timestamp()
            self.information["last_autosave_datetime"] = current_time.strftime("%c")

        # We save the administration file.
        self.administation.save()

    def end_management(self):
        """
        Manage what we do once all processes are stopped.
        """

        if not self.information["currently_under_test"]:
            self.information["previous_stats"] = self.information["current_stats"]
            del self.information["current_stats"]

        self.administation.save()

        if path.isdir(Outputs.current_directory + "db_types"):
            rmtree(Outputs.current_directory + "db_types")

        self.our_pyfunceble.pyfunceble.core.CLI.sort_generated_files()

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
        counters = {
            status_map[x]: len(y) for x, y in continue_data.items() if x in status_map
        }

        # We  complete with the status which are not found locally.
        counters.update({x: 0 for x in status_map.values() if x not in counters})
        # We set the number of tested.
        counters["tested"] = sum(counters.values())

        logging.info(counters)

        if "current_stats" not in self.information:
            self.information["current_stats"] = {"counter": counters, "builds": 1}
        else:
            self.information["current_stats"]["counter"] = counters
            self.information["current_stats"]["builds"] += 1

        # We ask PyFunceble to generate the percentage file.
        self.our_pyfunceble.generate_percentage_file(counters)

    def update_clean_list(self):
        """
        Update the content of the clean list.
        """

        if not self.information["currently_under_test"]:
            logging.info(
                "Started the generation of {0}".format(repr(self.clean_file.file))
            )

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

                self.information["current_stats"]["clean.list"] = len(clean_list)
                self.information["current_stats"]["domains.list"] = self.information[
                    "current_stats"
                ]["counter"]["tested"]

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

            self.information["current_stats"]["whitelisted.list"] = len(
                whitelisted_list
            )

            logging.info(
                "Finished the generation of {0}".format(
                    repr(self.whitelisted_file.file)
                )
            )

    def update_volatile_list(self):
        """
        Update the content of the volatile list.
        """

        logging.info(
            "Started the generation of {0}".format(repr(self.volatile_file.file))
        )

        if not self.information["currently_under_test"]:

            volatile_list = []

            if self.temp_volatile_file.exists():
                # The input file exists.

                # We get its content into list format.
                volatile_list.extend(self.temp_volatile_file.to_list())

            # We append the content of the previously whitelisted list.
            volatile_list.extend(self.whitelisted_file.to_list())
        else:
            volatile_list = self.volatile_file.to_list()

        # We whitelist the final content content.
        volatile_list = clean_list_with_official_whitelist(
            volatile_list, multiprocessing=True, processes=60
        )

        # We remove any duplicated.
        volatile_list = List(volatile_list).format(delete_empty=True)
        # We finaly save everything into the destination.
        self.volatile_file.write("\n".join(volatile_list), overwrite=True)

        self.information["current_stats"]["volatile.list"] = len(volatile_list)

        logging.info(
            "Finished the generation of {0}".format(repr(self.volatile_file.file))
        )

    def update_ip_list(self):
        """
        Update the content of the ip list.
        """

        input_file = File(Outputs.ip_subjects_destination)

        if not self.information["currently_under_test"]:
            logging.info(
                "Started the generation of {0}".format(repr(self.ip_file.file))
            )

            clean_count = 0
            ip_list = []
            clean_backup_location = self.clean_file.file + ".bak"
            self.ip_file.write("", overwrite=True)

            if input_file.exists():
                with open(input_file.file, "r", encoding="utf-8") as file_stream:
                    for line in file_stream:
                        line = line.strip()
                        if not line:
                            continue

                        if line.startswith("#"):
                            continue

                        ip_list.append(line.split()[-1])
                        self.ip_file.write(ip_list[-1] + "\n")

                with open(
                    self.clean_file.file, "r", encoding="utf-8"
                ) as clean_filestream, open(
                    clean_backup_location, "w", encoding="utf-8"
                ) as backed_clean_filestream:
                    for clean_line in clean_filestream:
                        clean_line = clean_line.strip()

                        if clean_line in ip_list:
                            continue

                        backed_clean_filestream.write(f"{clean_line}\n")
                        clean_count += 1

                move(clean_backup_location, self.clean_file.file)
                self.information["current_stats"]["clean.list"] = clean_count

            self.information["current_stats"]["ip.list"] = len(ip_list)

            logging.info(
                "Finished the generation of {0}".format(repr(self.ip_file.file))
            )

    def process(self):
        """
        Processes the whole logic.
        """

        logging.info("Starting process...")
        logging.info("Multiprocess Activated: {0}".format(self.multiprocessing))
        logging.info("Maximal number of processes: {0}".format(self.processes))

        # We get the current time as start time.
        start_time = int(datetime.now().timestamp())
        # We calculate the end time in second.
        end_time = start_time + (
            InfrastructrePyFuncebleConfiguration.configuration["ci_autosave_minutes"]
            * 60
        )

        logging.info("Start time: {0}".format(start_time))
        logging.info("End of test (push): {0}".format(end_time))

        if self.multiprocessing:
            with Pool(self.processes) as pool:
                to_test = []

                for extracted in pool.starmap(
                    self._extract_domains_from_line,
                    zip(
                        File(Outputs.input_destination).to_list(),
                        repeat(self.our_pyfunceble.pyfunceble.converter.File),
                    ),
                ):
                    if not extracted:
                        continue

                    if isinstance(extracted, list):
                        to_test.extend(extracted)
                    else:
                        to_test.append(extracted)
        else:
            # We get the list to test.
            to_test = [
                self._extract_domains_from_line(
                    x, self.our_pyfunceble.pyfunceble.converter.File
                )
                for x in File(Outputs.input_destination).to_list()
                if x and not x.startswith("#")
            ]

        # We save the formatted dataset
        File(Outputs.input_destination).write(
            "\n".join(List(to_test).format(delete_empty=True)), overwrite=True
        )

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
                set(to_test)
                - set([y for x in continue_data.values() for y in x])
                - self.our_pyfunceble.inactive_db.get_to_retest()
                - self.our_pyfunceble.inactive_db.get_already_tested()
            ),
            self.our_pyfunceble.inactive_db.get_to_retest(),
        )

        if not self.information["currently_under_test"]:
            # We are not currently under test.

            current_time = datetime.now()

            # We set that we now are under test.
            self.information["currently_under_test"] = True

            # We save the start epoche and datetime.
            self.information["start_epoch"] = current_time.timestamp()
            self.information["start_datetime"] = current_time.strftime("%c")

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

        logging.info("Finished process")

        # We set/create the percentage file.
        self.set_percentage()

        # We update/create the clean list.
        self.update_clean_list()

        # We update/create the whitelisted list.
        self.update_whitelisted_list()

        # We update/create the whitelisted list.
        self.update_volatile_list()

        # We update/create the ip list.
        self.update_ip_list()

        # And we manage the end of the tool.
        self.end_management()
