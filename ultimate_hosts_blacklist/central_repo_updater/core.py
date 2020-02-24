"""
The tool to update the central repository of the Ultimate-Hosts-Blacklist project.

Provide the brain of the program.

License:
::


    MIT License

    Copyright (c) 2019, 2020 Ultimate-Hosts-Blacklist
    Copyright (c) 2019, 2020 Nissar Chababy
    Copyright (c) 2019, 2020 Mitchell Krog

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


from os import cpu_count, environ
from os import sep as directory_separator
from os import walk
from tempfile import NamedTemporaryFile, TemporaryDirectory
from time import sleep

import PyFunceble
from PyFunceble.core.multiprocess import OurProcessWrapper, active_children
from PyFunceble.engine import ci
from requests import get

from ultimate_hosts_blacklist.central_repo_updater import logging
from ultimate_hosts_blacklist.central_repo_updater.clean import Clean
from ultimate_hosts_blacklist.central_repo_updater.deploy import Deploy
from ultimate_hosts_blacklist.central_repo_updater.generate import Generate
from ultimate_hosts_blacklist.central_repo_updater.repositories import (
    GitHub,
    Infrastructure,
    Output,
    Repositories,
)
from ultimate_hosts_blacklist.helpers import Dict
from ultimate_hosts_blacklist.whitelist.core import Core as WhitelistCore


class Core:
    """
    Brain of the program.

    :param multiprocessing: Allow us to use multiprocessing.
    :type multiprocessing: bool
    """

    # Will save what we write into repos.json
    repos = []

    def __init__(self, multiprocessing=False, processes=None):
        environ["PYFUNCEBLE_CONFIG_DIR"] = TemporaryDirectory().name
        PyFunceble.load_config(
            custom={
                "ci": True,
                "dns_server": ["one.one.one.one"],
                "ci_autosave_final_commit": Infrastructure.version,
            }
        )

        self.ci_engine = ci.TravisCI()
        self.ci_engine.init()
        self.ci_engine.permissions()

        self.multiprocessing = multiprocessing
        self.processes = cpu_count() if not processes else processes

        self.repositories = Repositories().get()

        logging.info("Multiprocess: %s", self.multiprocessing)
        logging.info("Processes: %s", self.processes)

        if self.multiprocessing:
            self.whitelisting_core = WhitelistCore(
                multiprocessing=True, processes=self.processes
            )
        else:
            self.whitelisting_core = WhitelistCore()

        self.temp = {
            "ip_dir": TemporaryDirectory(),
            "domain_dir": TemporaryDirectory(),
            "ip_file": NamedTemporaryFile(),
            "domain_file": NamedTemporaryFile(),
        }

        logging.info("Temporary IP Dir: %s", self.temp["ip_dir"].name)
        logging.info("Temporary Domain Dir: %s", self.temp["domain_dir"].name)
        logging.info("Temporary IP file: %s", self.temp["ip_file"].name)
        logging.info("Temporary Domain file: %s", self.temp["domain_file"].name)

        self.get_list(next(self.repositories), self.whitelisting_core, self.temp)

    @classmethod
    def get_list(cls, repository_info, whitelisting_core, temp):
        """
        Get the list to process from the given repository_info.
        """

        logging.info(
            "Trying to get the right file for the %s input source.",
            repr(repository_info["name"]),
        )

        url_base = GitHub.partial_raw_link % repository_info["name"]

        ip_url = f"{url_base}ip.list"
        whitelisted_url = f"{url_base}whitelisted.list"
        input_url = f"{url_base}domains.list"

        req_white = get(whitelisted_url)
        req_ip = get(ip_url)

        ip_result = None
        domain_result = []

        if req_ip.status_code == 200:
            logging.info("Could get `ip.list` of %s.", repr(repository_info["name"]))

            ip_result = req_ip.text.splitlines()
        else:
            logging.critical(
                "Unable to get `ip.list` from %s.", repr(repository_info["name"])
            )

        if req_white.status_code == 200:
            logging.info(
                "Could get `whitelisted.list` of %s.", repr(repository_info["name"])
            )

            domain_result = req_white.text.splitlines()
        else:
            req = get(input_url)

            if req.status_code == 200:
                logging.info(
                    "Could get `domains.list` of %s.", repr(repository_info["name"])
                )
                logging.info(
                    "Starting whitelisting of %s", repr(repository_info["name"])
                )

                domain_result = whitelisting_core.filter(
                    string=req.text, already_formatted=True
                )

                logging.info(
                    "Finished whitelisting of %s.", repr(repository_info["name"])
                )
            else:
                logging.critical(
                    "Unable to get a list from %s.", repr(repository_info["name"])
                )

        if ip_result is None:
            ip_result = []
            api = PyFunceble.core.API(None)

            for index, line in enumerate(domain_result):
                api.subject = line
                if line in ip_result or api.ipv4_syntax():
                    ip_result.append(line)
                    del domain_result[index]

            if ip_result:
                logging.info(
                    "Found some IPs in the domain list of %s.",
                    repr(repository_info["name"]),
                )

        logging.info(
            "Starting whitelisting of the IP list of %s.", repr(repository_info["name"])
        )
        ip_result = whitelisting_core.filter(items=ip_result, already_formatted=True)
        logging.info(
            "Finished whitelisting of the IP list of %s.", repr(repository_info["name"])
        )

        logging.info(
            "Starting whitelisting of the domain list of %s.",
            repr(repository_info["name"]),
        )
        domain_result = whitelisting_core.filter(
            items=domain_result, already_formatted=True
        )
        logging.info(
            "Finished whitelisting of the ip list of %s.", repr(repository_info["name"])
        )

        logging.info(
            "Starting backup of the list of domains of %s.",
            repr(repository_info["name"]),
        )
        with open(
            f'{temp["domain_dir"].name}{directory_separator}{repository_info["name"]}',
            "w",
        ) as file_stream:
            file_stream.write("\n".join(domain_result) + "\n")
        logging.info(
            "Finished backup of the list of domains of %s.",
            repr(repository_info["name"]),
        )

        logging.info(
            "Starting backup of the list of ip of %s.", repr(repository_info["name"])
        )
        with open(
            f'{temp["ip_dir"].name}{directory_separator}{repository_info["name"]}', "w"
        ) as file_stream:
            file_stream.write("\n".join(ip_result) + "\n")
        logging.info(
            "Finished backup of the list of domains of %s.",
            repr(repository_info["name"]),
        )

    def get_them(self):
        """
        Get all needed lists.
        """

        repos = []
        finished = False

        if self.multiprocessing:
            while True:
                while len(active_children()) < self.processes:
                    try:
                        repository = next(self.repositories)
                        process = OurProcessWrapper(
                            target=self.get_list,
                            args=(repository, self.whitelisting_core, self.temp),
                        )

                        process.name = f'Get {repository["name"]}'
                        process.start()
                        repos.append(repository)

                    except StopIteration:
                        finished = True
                        break

                if finished:
                    while "Get" in " ".join([x.name for x in active_children()]):
                        continue

                    break
        else:
            for repository in self.repositories:
                repos.append(repository)
                self.get_list(repository, self.whitelisting_core, self.temp)

        logging.info("Saving the list of repositories.")
        Dict(repos).to_json(Output.repos_file)

    def merge_them(self):
        """
        Merge all lists.
        """

        for root, _, files in walk(self.temp["ip_dir"].name):
            for file in files:
                with open(f"{root}{directory_separator}{file}", "rb") as file_stream:
                    self.temp["ip_file"].write(file_stream.read())
                    logging.info(
                        "Merged %s into %s (ip_file)", file, self.temp["ip_file"].name
                    )

        for root, _, files in walk(self.temp["domain_dir"].name):
            for file in files:
                with open(f"{root}{directory_separator}{file}", "rb") as file_stream:
                    self.temp["domain_file"].write(file_stream.read())
                    logging.info(
                        "Merged %s into %s (domain_file)",
                        file,
                        self.temp["domain_file"].name,
                    )

    def process(self):
        """
        Process the repository update.
        """

        self.get_them()
        self.merge_them()

        with open(self.temp["domain_file"].name, "r") as domain_filestream, open(
            self.temp["ip_file"].name, "r"
        ) as ip_filestream:
            domains = [
                x
                for x in PyFunceble.helpers.List(
                    domain_filestream.read().splitlines()
                ).custom_format(PyFunceble.engine.Sort.standard)
                if x
            ]

            ips = [
                x
                for x in PyFunceble.helpers.List(
                    ip_filestream.read().splitlines()
                ).custom_format(PyFunceble.engine.Sort.standard)
                if x
            ]

        Generate.dotted(domains)
        Generate.plain_text_domain(domains)
        Generate.plain_text_ip(ips)
        Generate.unix_hosts(domains)
        Generate.windows_hosts(domains)
        Generate.hosts_deny(ips)
        Generate.superhosts_deny(domains + ips)
        Generate.readme_md(len(domains), len(ips))

        self.temp["ip_dir"].cleanup()
        self.temp["domain_dir"].cleanup()
        Clean()

        deployment = Deploy(self.ci_engine)

        deployment.github()
        sleep(3)
        deployment.hosts_ubuntu101_co_za()
