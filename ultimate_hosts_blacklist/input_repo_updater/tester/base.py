"""
The tool to update the input repositories of the Ultimate-Hosts-Blacklist project.

Provides the base of all testers.

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
from datetime import datetime, timedelta
from os import cpu_count
from shutil import move

import PyFunceble

from ultimate_hosts_blacklist.whitelist import clean_list_with_official_whitelist

from ..administration import Administration
from ..config import OurPyFuncebleConfig, Outputs
from ..installer import DomainsListInstaller


class TesterBase:
    """
    Provides everything the tester might need.
    """

    # pylint: disable=too-many-instance-attributes

    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state

        if not PyFunceble.CONFIGURATION:
            PyFunceble.load_config(
                generate_directory_structure=not PyFunceble.helpers.Directory(
                    Outputs.output_destination
                ).exists(),
                custom=OurPyFuncebleConfig.api_configuration,
            )

        if not hasattr(self, "start_time"):
            self.start_time = datetime.now()
            self.end_time = self.start_time + timedelta(
                seconds=PyFunceble.CONFIGURATION.ci_autosave_minutes * 60
            )
            logging.info("Start time: %s", self.start_time.isoformat())
            logging.info("End time (approx.): %s", self.end_time.isoformat())

        if not hasattr(self, "administration"):
            self.administration = Administration()
            self.multiprocessing = False
            self.processes = cpu_count()

            DomainsListInstaller(self.administration.raw_link, processes=self.processes)

        if not hasattr(self, "auto_continue"):
            self.auto_continue = PyFunceble.engine.AutoContinue(
                "api_call", parent_process=False
            )
            self.api_core = PyFunceble.core.API(
                None,
                complete=True,
                configuration=OurPyFuncebleConfig.api_configuration,
                is_parent=False,
            )
            self.ci_engine = PyFunceble.engine.AutoSave.get_current_ci()

            if self.ci_engine:
                self.ci_engine.init()

        if not hasattr(self, "temp_volatile_file"):
            self.temp_volatile_file = PyFunceble.helpers.File(
                Outputs.temp_volatile_destination
            )
            self.clean_file = PyFunceble.helpers.File(Outputs.clean_destination)
            self.whitelited_file = PyFunceble.helpers.File(
                Outputs.whitelisted_destination
            )
            self.volatile_file = PyFunceble.helpers.File(Outputs.volatile_destination)
            self.ip_file = PyFunceble.helpers.File(Outputs.ip_destination)

        if not self.administration.currently_under_test:
            current_time = datetime.now()
            self.administration.currently_under_test = True
            self.administration.start_epoch = current_time
            self.administration.start_datetime = current_time

            self.administration.save()

    @classmethod
    def should_it_be_ignored(cls, subject, auto_continue, inactive_db):
        """
        Checks if the given subject should be ignored.
        """

        if not subject:
            return True

        if subject.startswith("#"):
            return True

        if subject in auto_continue.get_already_tested():
            return True

        if subject in inactive_db.get_already_tested():
            return True

        return False

    def generate_percentage_file(self):
        """
        Generate the percentage file.
        """

        # status_map = {"ACTIVE": "up", "INACTIVE": "down", "INVALID": "invalid"}

        self.auto_continue.parent = True
        self.auto_continue.update_counters()
        self.auto_continue.parent = False

        PyFunceble.output.Percentage().log()

        if "current_stats" not in self.administration:
            self.administration.current_stats = {
                "counter": PyFunceble.INTERN["counter"]["number"],
                "builds": 1,
            }
        else:
            self.administration.current_stats["counter"] = PyFunceble.INTERN["counter"][
                "number"
            ]
            self.administration.current_stats["builds"] += 1

    @classmethod
    def test_with_pyfunceble(cls, subject, api_core):
        """
        Returns the test result (directly from PyFunceble).
        """

        api_core.subject = subject

        return api_core.domain_and_ip()

    def test(
        self, subject, api_core, auto_continue, inactive_db, whois_db
    ):  # pylint: disable=too-many-arguments
        """
        Do the test and generate what needs to be geneated.
        """

        test_result = self.test_with_pyfunceble(subject, api_core)
        coloration = PyFunceble.core.CLI.get_simple_coloration(test_result["status"])

        if (
            test_result["_status"] != test_result["status"]
            or test_result["_status_source"] != test_result["status_source"]
        ):
            self.temp_volatile_file.write(f"{subject}\n", overwrite=False)

        print(
            f"{coloration}{repr(subject)} "
            f"is {test_result['status']} "
            f"({test_result['status_source']} - {test_result['http_status_code']})"
        )

        auto_continue.add(subject, test_result["status"])

        if test_result["status"] != "ACTIVE":
            inactive_db.add(subject, test_result["status"])

        if test_result["expiration_date"] or test_result["whois_record"]:
            whois_db.add(subject, test_result["expiration_date"])

    @classmethod
    def check_exception(cls, processes):
        """
        Check if an exception is present into the given pool of processes.

        :param list processes. A list of running processes.
        """

        exception_present = False
        traceback = None

        for process in processes:
            if exception_present:
                process.terminate()
                continue

            try:
                if process.exception and not exception_present:
                    _, traceback = process.exception
                    print(traceback)
                    logging.error(traceback)

                    exception_present = True
            except (AttributeError, OSError):
                continue

        if exception_present:
            print(traceback)
            sys.exit(1)

    def save_all(self):
        """
        Saves everything which was in memory.
        """

        self.generate_percentage_file()
        self.update_clean_list()
        self.update_whitelisted_list()
        self.update_volatile_list()
        self.update_ip_list()

        self.api_core.inactive_db.parent = True
        self.api_core.inactive_db.save()
        self.api_core.inactive_db.parent = False

        self.api_core.whois_db.parent = True
        self.api_core.whois_db.save()
        self.api_core.whois_db.parent = False

        if self.administration.currently_under_test:
            self.auto_continue.parent = True
            self.auto_continue.save()
            self.auto_continue.parent = False

        self.clean_uneeded()
        PyFunceble.core.CLI.sort_generated_files()

        self.administration.save()

        self.push_back_to_repo()

    def clean_uneeded(self):
        """
        Cleans everything undeeded.
        """

        if not self.administration.currently_under_test:
            self.administration.previous_stats = self.administration.current_stats
            del self.administration.current_stats

        file_to_delete = []
        dirs_to_delete = [Outputs.current_directory + "db_types"]

        for file in file_to_delete:
            PyFunceble.helpers.File(file).delete()

        for directory in dirs_to_delete:
            PyFunceble.helpers.Directory(directory).delete()

    def push_back_to_repo(self):
        """
        Pushes back to the repository.
        """

        if self.ci_engine:
            if self.administration.currently_under_test:
                logging.info("Still some data to test.")
                logging.info("Launching auto continue commit/push and exit.")

                self.ci_engine.not_end_commit()
            else:
                logging.info("Test finished.")
                logging.info("Launching auto save commit/push and exit.")

                self.ci_engine.end_commit()

    def are_we_allowed_to_continue(self):
        """
        Checks if we are allowed to continue.
        """

        return datetime.now() < self.end_time

    def update_clean_list(self):
        """
        Updates the content of the clean list.
        """

        input_file = PyFunceble.helpers.File(Outputs.active_subjects_destination)

        if not self.administration.currently_under_test and input_file.exists():
            logging.info("Started the generation of %s.", repr(self.clean_file.path))

            clean_list = PyFunceble.helpers.List(
                PyFunceble.helpers.Regex(r"^#|^\s*$").get_not_matching_list(
                    input_file.read().splitlines()
                )
            ).custom_format(PyFunceble.engine.Sort.standard)

            self.clean_file.write("\n".join(clean_list) + "\n", overwrite=True)

            self.administration.current_stats["clean_list"] = len(clean_list)
            self.administration.current_stats["domains.list"] = len(
                PyFunceble.helpers.File(Outputs.input_destination).read().splitlines()
            )

            logging.info("Finished the generation of %s", repr(self.clean_file.path))

    def update_whitelisted_list(self):
        """
        Updates the whitelisted list.
        """

        if self.clean_file.exists():
            logging.info(
                "Started the generation of %s.", repr(self.whitelited_file.path)
            )

            whitelisted_list = clean_list_with_official_whitelist(
                self.clean_file.read().splitlines(),
                multiprocessing=True,
                processes=self.processes
                if not PyFunceble.helpers.EnvironmentVariable(
                    "TRAVIS_BUILD_DIR"
                ).exists()
                else 60,
            )

            self.whitelited_file.write(
                "\n".join(whitelisted_list) + "\n", overwrite=True
            )

            self.administration.current_stats["whitelisted.list"] = len(
                whitelisted_list
            )
            logging.info(
                "Finished the generation of %s.", repr(self.whitelited_file.path)
            )

    def update_volatile_list(self):
        """
        Update the volatile list.
        """

        logging.info("Started the generation of %s.", repr(self.volatile_file.path))
        if not self.administration.currently_under_test:
            volatile_list = []

            if self.temp_volatile_file.exists():
                volatile_list.extend(self.temp_volatile_file.read().splitlines())

            if self.whitelited_file.exists():
                volatile_list.extend(self.whitelited_file.read().splitlines())
        else:
            volatile_list = self.volatile_file.read().splitlines()

        volatile_list = PyFunceble.helpers.List(
            clean_list_with_official_whitelist(
                volatile_list,
                multiprocessing=True,
                processes=self.processes
                if not PyFunceble.helpers.EnvironmentVariable(
                    "TRAVIS_BUILD_DIR"
                ).exists()
                else 60,
            )
        ).custom_format(PyFunceble.engine.Sort.standard)

        self.volatile_file.write("\n".join(volatile_list) + "\n", overwrite=True)

        self.administration.current_stats["volatile.list"] = len(volatile_list)

        logging.info("Finished the generation of %s.", repr(self.volatile_file.path))

    def update_ip_list(self):
        """
        Updates the content of the ip list.
        """

        input_file = PyFunceble.helpers.File(Outputs.ip_subjects_destination)

        if not self.administration.currently_under_test:
            logging.info("Started the generation of %s.", repr(self.ip_file.path))
            self.ip_file.write("", overwrite=True)

            if input_file.exists():
                clean_count = 0
                ip_list = []
                clean_backup_location = self.clean_file.path + ".bak"

                with open(input_file.path, "r", encoding="utf-8") as file_stream:
                    for line in file_stream:
                        line = line.strip()

                        if not line:
                            continue

                        if line.startswith("#"):
                            continue

                        ip_list.append(line.split()[-1])
                        self.ip_file.write(ip_list[-1] + "\n")

                with open(
                    self.clean_file.path, "r", encoding="utf-8"
                ) as clean_filestream, open(
                    clean_backup_location, "w", encoding="utf-8"
                ) as backed_clean_filestream:
                    for clean_line in clean_filestream:
                        clean_line = clean_line.strip()

                        if clean_line in ip_list:
                            continue

                        backed_clean_filestream.write(f"{clean_line}\n")
                        clean_count += 1

                move(clean_backup_location, self.clean_file.path)
                self.administration.current_stats["clean.list"] = clean_count
                self.administration.current_stats["ip.list"] = len(ip_list)

            logging.info("Finished the generation of %s.", repr(self.ip_file.path))
