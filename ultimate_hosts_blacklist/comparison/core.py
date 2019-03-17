"""
The comparison tool of the Ultimate-Hosts-Blacklist project.

Brain of the comparison.

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

# pylint: disable=logging-format-interpolation, bad-continuation
import logging
from os import path

from PyFunceble import ipv4_syntax_check, syntax_check

from ultimate_hosts_blacklist.comparison.configuration import Configuration
from ultimate_hosts_blacklist.helpers import Download, File, List


class Core:
    """
    Brain of the tool.

    :param your_domains_and_ips: The list of domains/ips from the source.
    :type your_domains_and_ips: list

    :param use_cache: Tell us if we use the cache version (if exists).
    :type use_cache: bool
    """

    def __init__(self, your_domains_and_ips, use_cache=False, verbose=False):
        self.verbose = verbose
        self.cache = use_cache

        if self.verbose:
            logging.basicConfig(format="%(asctime)s: %(levelname)s - %(message)s", level=logging.INFO)
        else:
            logging.basicConfig()

        self.data = {
            "not_present": {
                "domains": 0,
                "ips": 0,
                "items": {"ips": [], "domains": []},
                "overall": 0,
                "percentage": {"domains": 0, "ips": 0, "overall": 0},
            },
            "our": {
                "domains": 0,
                "ips": 0,
                "items": {"ips": [], "domains": []},
                "overall": 0,
                "percentage": {"domains": 0, "ips": 0},
            },
            "your": {
                "domains": 0,
                "ips": 0,
                "items": {"ips": [], "domains": []},
                "overall": 0,
                "percentage": {"domains": 0, "ips": 0},
            },
        }

        self.data["our"]["items"]["ips"] = self.get_our_ips()
        self.data["our"]["items"]["domains"] = self.get_our_domains()

        if your_domains_and_ips and isinstance(your_domains_and_ips, list):
            self.data["your"]["items"]["domains"], self.data["your"]["items"][
                "ips"
            ] = self.__separate_ips_from_domains(your_domains_and_ips)
        else:
            raise TypeError("`your_domains_and_ips` must be {0}".format(type(list)))

    @classmethod
    def __separate_ips_from_domains(cls, data):
        """
        Given a list of domains or ips, we return a tuple
        with the list of IPs and another with the list of domains.

        :param data: Your list of domains and ips.
        :type data: list

        :return: (your list of domains, your list of IPs)
        :rtype: tuple
        """

        logging.info("Separating domains and ips from your list.")
        your_ips = []
        your_domains = []

        for element in data:
            if ipv4_syntax_check(element):
                your_ips.append(element)
            elif syntax_check(element):
                your_domains.append(element)

        return your_domains, your_ips

    @classmethod
    def format_line(cls, line):
        """
        This method format a line so that we get abstraction of what is not
        a domain or IP.


        :param line: The line to format.
        :type line: str

        :return: The formatted line.
        :rtype: str
        """

        if not line.startswith("#"):

            if "#" in line:
                line = line[: line.find("#")].strip()

            if " " in line or "\t" in line:
                splited_line = line.split()

                index = 1
                while index < len(splited_line):
                    if splited_line[index]:
                        break

                    index += 1

                return splited_line[index]

            return line

        return ""

    def get_our_domains(self):
        """
        Download an return the list of domains.
        """

        destination = "domains.list"

        if self.cache and path.isfile(destination):
            logging.info(
                "Getting our list of domains from {0}.".format(repr(destination))
            )

            return File(destination).to_list()

        logging.info(
            "Getting our list of domains from {0}.".format(
                repr(Configuration.LINKS["domains"])
            )
        )
        our_domains = Download(Configuration.LINKS["domains"], None).link()

        if isinstance(our_domains, str):
            if self.cache:
                logging.info(
                    "Saving our list of domains into {0}".format(repr(destination))
                )
                File(destination).write(our_domains, overwrite=True)

            logging.info("Formatting our list of domains.")
            return List(our_domains.split("\n")).format()

        raise Exception(
            "Unable to download {0}".format(repr(Configuration.LINKS["domains"]))
        )

    def get_our_ips(self):
        """
        Download an return the list of ips.
        """

        destination = "ips.list"

        if self.cache and path.isfile(destination):
            logging.info("Getting our list of IPs from {0}.".format(repr(destination)))

            return File(destination).to_list()

        logging.info(
            "Getting our list of IPs from {0}.".format(
                repr(Configuration.LINKS["domains"])
            )
        )
        our_ips = Download(Configuration.LINKS["ips"], None).link()

        if isinstance(our_ips, str):
            if self.cache:
                logging.info(
                    "Saving our list of IPs into {0}".format(repr(destination))
                )
                File(destination).write(our_ips, overwrite=True)

            logging.info("Formatting our list of IPs.")
            return List(our_ips.split("\n")).format()

        raise Exception(
            "Unable to download {0}".format(repr(Configuration.LINKS["ips"]))
        )

    def count(self):
        """
        Process the count and return a dict with all our data.
        """

        logging.info("Getting the list of non present domains.")
        self.data["not_present"]["items"]["domains"] = list(
            set(self.data["your"]["items"]["domains"])
            - set(self.data["our"]["items"]["domains"])
        )

        logging.info("Getting the list of non present IPs.")
        self.data["not_present"]["items"]["ips"] = list(
            set(self.data["your"]["items"]["ips"])
            - set(self.data["our"]["items"]["ips"])
        )

        logging.info("Getting our number of domains.")
        self.data["our"]["domains"] = len(self.data["our"]["items"]["domains"])

        logging.info("Getting our number of IPs.")
        self.data["our"]["ips"] = len(self.data["our"]["items"]["ips"])

        logging.info("Calculating our total number.")
        self.data["our"]["overall"] = (
            self.data["our"]["domains"] + self.data["our"]["ips"]
        )

        logging.info("Calculating our percentage of domains.")
        self.data["our"]["percentage"]["domains"] = (
            self.data["our"]["domains"] * 100
        ) / self.data["our"]["overall"]

        logging.info("Calculating our percentage of IPs.")
        self.data["our"]["percentage"]["ips"] = (
            self.data["our"]["ips"] * 100
        ) / self.data["our"]["overall"]

        logging.info("Getting your number of domains.")
        self.data["your"]["domains"] = len(self.data["your"]["items"]["domains"])

        logging.info("Getting your number of IPs.")
        self.data["your"]["ips"] = len(self.data["your"]["items"]["ips"])

        logging.info("Calculating your total number.")
        self.data["your"]["overall"] = (
            self.data["your"]["domains"] + self.data["your"]["ips"]
        )

        logging.info("Calculating your percentage of domains.")
        self.data["your"]["percentage"]["domains"] = (
            self.data["your"]["domains"] * 100
        ) / self.data["your"]["overall"]

        logging.info("Calculating your percentage of IPs.")
        self.data["your"]["percentage"]["ips"] = (
            self.data["your"]["ips"] * 100
        ) / self.data["your"]["overall"]

        logging.info("Getting your number of non present domains.")
        self.data["not_present"]["domains"] = len(
            self.data["not_present"]["items"]["domains"]
        )

        logging.info("Getting your number of non present IPs.")
        self.data["not_present"]["ips"] = len(self.data["not_present"]["items"]["ips"])

        logging.info("Getting your number of non present.")
        self.data["not_present"]["overall"] = (
            self.data["not_present"]["domains"] + self.data["not_present"]["ips"]
        )

        logging.info("Calculating your percentage of non present domains.")
        self.data["not_present"]["percentage"]["domains"] = (
            self.data["not_present"]["domains"] * 100
        ) / self.data["your"]["overall"]

        logging.info("Calculating your percentage of non present IPs.")
        self.data["not_present"]["percentage"]["ips"] = (
            self.data["not_present"]["ips"] * 100
        ) / self.data["your"]["overall"]

        logging.info("Calculating your percentage of non present.")
        self.data["not_present"]["percentage"]["overall"] = (
            self.data["not_present"]["percentage"]["domains"]
            + self.data["not_present"]["percentage"]["ips"]
        )

        return self.data
