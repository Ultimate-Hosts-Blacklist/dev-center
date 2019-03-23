"""
The tool to update the central repository of the Ultimate-Hosts-Blacklist project.

Provide the brain of the program.

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
# pylint: disable=bad-continuation, inconsistent-return-statements
from os import cpu_count
from time import sleep

from PyFunceble import ipv4_syntax_check, syntax_check
from requests import get

from ultimate_hosts_blacklist.central_repo_updater import logging
from ultimate_hosts_blacklist.central_repo_updater.clean import Clean
from ultimate_hosts_blacklist.central_repo_updater.configuration import GitHub, Output
from ultimate_hosts_blacklist.central_repo_updater.deploy import Deploy
from ultimate_hosts_blacklist.central_repo_updater.generate import Generate
from ultimate_hosts_blacklist.central_repo_updater.repositories import Repositories
from ultimate_hosts_blacklist.helpers import Dict, List, TravisCI
from ultimate_hosts_blacklist.whitelist.core import Core as WhitelistCore


class Core:
    """
    Brain of the program.

    :param multiprocessing: Allow us to use multiprocessing.
    :type multiprocessing: bool
    """

    # Will save what we write into repos.json
    repos = []

    def __init__(self, multiprocessing=True, processes=None):
        TravisCI().configure_git_repo()
        TravisCI().fix_permissions()

        self.multiprocessing = multiprocessing

        if self.multiprocessing:
            logging.info("multiprocessing activated.")
            self.repositories = list(Repositories().get())

            if not processes:
                cpu_numbers = cpu_count()

                if cpu_numbers is not None:
                    self.processes = cpu_numbers
                else:
                    self.processes = len(self.repositories) // 2 % 10
            else:
                self.processes = processes
            logging.info(
                "Using {0} simultaneous processes.".format(repr(self.processes))
            )
        else:
            self.repositories = Repositories().get()

        if self.multiprocessing:
            self.whitelisting_core = WhitelistCore(
                multiprocessing=True, processes=self.processes // 2
            )
        else:
            self.whitelisting_core = WhitelistCore()

    @classmethod
    def __separate_domains_from_ip(cls, cleaned_list):
        """
        Given a cleaned list, we separate domains from IP.
        """

        logging.info("Getting the list of domains.")
        domains = [x for x in set(cleaned_list) if x and syntax_check(x)]
        temp = set(cleaned_list) - set(domains)

        logging.info("Getting the list of IPs.")
        return (domains, [x for x in temp if x and ipv4_syntax_check(x)])

    def get_list(self, repository_info):
        """
        Get the list from the input source.
        """

        logging.info(
            "Trying to get domains and ips from {0} input source.".format(
                repr(repository_info["name"])
            )
        )

        url_base = GitHub.partial_raw_link % repository_info["name"]
        clean_url = "{0}clean.list".format(url_base)
        non_clean_url = "{0}domains.list".format(url_base)

        req = get(clean_url)

        if req.status_code == 200:
            logging.info(
                "Could get `clean.list` of {0}.".format(repr(repository_info["name"]))
            )
            logging.info(
                "Starting whitelisting of {0}.".format(repr(repository_info["name"]))
            )
            result = self.whitelisting_core.filter(
                string=req.text, already_formatted=True
            )
            logging.info(
                "Finished whitelisting of {0}.".format(repr(repository_info["name"]))
            )
        else:
            req = get(non_clean_url)

            if req.status_code == 200:
                logging.info(
                    "Could get `domains.list` of {0}.".format(
                        repr(repository_info["name"])
                    )
                )
                logging.info(
                    "Starting whitelisting of {0}.".format(
                        repr(repository_info["name"])
                    )
                )
                result = self.whitelisting_core.filter(
                    string=req.text, already_formatted=True
                )
                logging.info(
                    "Finished whitelisting of {0}.".format(
                        repr(repository_info["name"])
                    )
                )
            else:
                raise Exception(
                    "Unable to get a list from {0}.".format(
                        repr(repository_info["name"])
                    )
                )

        return result

    def process_simple(self):
        """
        Process the repository update in a simple way.
        """

        all_domains = []
        all_ips = []

        repos = []

        for data in self.repositories:
            logging.debug(data)
            domains, ips = self.__separate_domains_from_ip(self.get_list(data))
            all_domains.extend(domains)
            all_ips.extend(ips)
            repos.append(data)

        logging.info("Saving the list of repositories.")
        Dict(repos).to_json(Output.repos_file)

        return (
            List(all_domains).format(delete_empty=True),
            List(all_ips).format(delete_empty=True),
        )

    def process(self):
        """
        Process the repository update.
        """

        domains, ips = self.process_simple()

        Generate.dotted(domains)
        Generate.plain_text_domain(domains)
        Generate.plain_text_ip(ips)
        Generate.unix_hosts(domains)
        Generate.windows_hosts(domains)
        Generate.hosts_deny(ips)
        Generate.superhosts_deny(domains + ips)
        Generate.readme_md(len(domains), len(ips))

        Clean()

        Deploy().github()
        sleep(3)
        Deploy().hosts_ubuntu101_co_za()
