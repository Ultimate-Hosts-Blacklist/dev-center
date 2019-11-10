"""
The comparison tool of the Ultimate-Hosts-Blacklist project.

The main entry.

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

import logging
import argparse
from os import path

from colorama import Fore, Style
from colorama import init as initiate_coloration

from ultimate_hosts_blacklist.comparison.configuration import Configuration
from ultimate_hosts_blacklist.comparison.core import Core
from ultimate_hosts_blacklist.helpers import Dict, Download, File
from ultimate_hosts_blacklist.whitelist import clean_list_with_official_whitelist

# Set our version.
VERSION = "1.2.0"


def response_from_data(data):
    """
    Produce the interpretation of the data.

    :param data: The data from the Core.
    :type data: dict
    """

    print("\n")
    print(
        Fore.GREEN + "Ultimate Hosts Blacklist: {0:,d}".format(data["our"]["overall"])
    )
    print(
        Fore.MAGENTA
        + "    IP: {0:,d} ({1:,.2f}%)".format(
            data["our"]["ips"], data["our"]["percentage"]["ips"]
        )
    )
    print(
        Fore.YELLOW
        + "    Domains: {0:,d} ({1:,.2f}%)".format(
            data["our"]["domains"], data["our"]["percentage"]["domains"]
        )
    )
    print(Fore.GREEN + "The list: {0:,d}".format(data["your"]["overall"]))
    print(
        Fore.MAGENTA
        + "    IP: {0:,d} ({1:,.2f}%)".format(
            data["your"]["ips"], data["your"]["percentage"]["ips"]
        )
    )
    print(
        Fore.YELLOW
        + "    Domains: {0:,d} ({1:,.2f}%)".format(
            data["your"]["domains"], data["your"]["percentage"]["domains"]
        )
    )
    print(
        Fore.GREEN
        + "Not present: {0:,d} ({1:,.2f}%)".format(
            data["not_present"]["overall"], data["not_present"]["percentage"]["overall"]
        )
    )
    print(
        Fore.MAGENTA
        + "    IP: {0:,d} ({1:,.2f}%)".format(
            data["not_present"]["ips"], data["not_present"]["percentage"]["ips"]
        )
    )
    print(
        Fore.YELLOW
        + "    Domains: {0:,d} ({1:,.2f}%)".format(
            data["not_present"]["domains"], data["not_present"]["percentage"]["domains"]
        )
    )

    return data


def get_to_compare(dataset, clean):
    """
    Given a dataset, we return the
    list we have to compare.

    :param list dataset:
        The dataset to work with.
    :param bool clean:
        The whitelisting authorization.
    :rtype: list
    """

    to_compare = []
    for line in dataset:
        logging.debug(f"Got line: {repr(line)}")

        if not line:
            logging.debug(f"Ignored line: {repr(line)}")
            continue

        extracted = Core.format_line(line)

        logging.debug(f"Extracted: {repr(extracted)}")

        if not extracted:
            logging.debug(f"Ignored extracted: {repr(extracted)}")
            continue

        if isinstance(extracted, list):
            to_compare.extend(extracted)
        else:
            to_compare.append(extracted)
        logging.debug(f"Added to the list of subject to compare: {repr(extracted)}")

    if clean and to_compare:
        logging.debug(f"Starting whitelisting of previously extracted data.")
        to_compare = clean_list_with_official_whitelist(to_compare)
        logging.debug(f"Finished whitelisting of previously extracted data.")

    return to_compare


def compare_file(file_path, cache=False, clean=False, export=False):
    """
    Given a file path, we make the comparison of its
    content with our infrastructure.

    :param file_path: The path of the file we are comparing.
    :type file_path: str

    :param cache: Activate/Deactivate the cache usage.
    :type cache bool

    :param clean:
        Activate/Deactivate the cleaning of with our whitelist before
        performing the comparison.
    :type clean: bool

    :param export:
        Activate/Deactive the production of a dump of all information.
    :type export bool
    """

    logging.debug(f"Starting extraction of {repr(file_path)}...")
    to_compare = get_to_compare(File(file_path).to_list(), clean)
    logging.debug(f"Finished extraction of {repr(file_path)}...")

    if export:
        Dict(response_from_data(Core(to_compare, use_cache=cache).count())).to_json(
            Configuration.EXPORT
        )
        logging.debug(f"Result exported into {Configuration.EXPORT}.")
    else:
        response_from_data(Core(to_compare, use_cache=cache).count())


def compare_link(link, cache=False, clean=False, export=False):
    """
    Given a link, we make the comparison of its
    content with our infrastructure.

    :param link: The link we are going to download and compare.
    :type link: str

    :param cache: Activate/Deactivate the cache usage.
    :type cache bool

    :param clean:
        Activate/Deactivate the cleaning of with our whitelist before
        performing the comparison.
    :type clean: bool

    :param export:
        Activate/Deactive the production of a dump of all information.
    :type export bool
    """

    data = Download(link, None).link()

    if isinstance(data, str):

        logging.debug(f"Starting extraction of {repr(link)}...")
        to_compare = get_to_compare(data.split("\n"), clean)
        logging.debug(f"Finished extraction of {repr(link)}...")

        if export:
            Dict(response_from_data(Core(to_compare, use_cache=cache).count())).to_json(
                Configuration.EXPORT
            )
            logging.debug(f"Result exported into {Configuration.EXPORT}.")
        else:
            response_from_data(Core(to_compare, use_cache=cache).count())
    else:
        raise Exception("Could not download {0}".format(repr(link)))


def compare_with_administration_file(cache=False, clean=False, export=False):
    """
    Look for the adminsitration file in the current
    directory, and execute based on the given info.

    :param cache: Activate/Deactivate the cache usage.
    :type cache bool

    :param clean:
        Activate/Deactivate the cleaning of with our whitelist before
        performing the comparison.
    :type clean: bool

    :param export:
        Activate/Deactive the production of a dump of all information.
    :type export bool
    """

    data = Dict.from_json(File(Configuration.INFO).read())

    if data and isinstance(data, dict):
        if "link" in data and data["link"]:
            compare_link(data["link"], cache=cache, clean=clean, export=export)
        elif "file" in data and data["file"]:
            compare_file(data["file"], cache=cache, clean=clean, export=export)


def _command_line():
    """
    Provide the CLI.
    """

    if __name__ == "ultimate_hosts_blacklist.comparison":
        initiate_coloration(autoreset=True)

        parser = argparse.ArgumentParser(
            description="A script to compare a given link or file to \
            Ultimate Hosts Blacklist infrastructure.",
            epilog="Crafted with %s by %s"
            % (
                Fore.RED + "♥" + Fore.RESET,
                Style.BRIGHT + Fore.CYAN + "Nissar Chababy (Funilrys)",
            ),
        )

        parser.add_argument(
            "-c",
            "--cache",
            action="store_true",
            default=False,
            help="Use cache if exist.",
        )
        parser.add_argument(
            "--clean",
            action="store_true",
            default=False,
            help="Clean the given file/link with our official whitelist tool before processing.",
        )
        parser.add_argument(
            "-e",
            "--export",
            action="store_true",
            default=False,
            help="Produce a JSON file with all complete information - including the list or domains and IPs which are not present.",  # pylint: disable=line-too-long
        )
        parser.add_argument("-f", "--file", type=str, help="File to compare.")
        parser.add_argument("-l", "--link", type=str, help="Link to compare.")
        parser.add_argument(
            "--verbose", action="store_true", default=False, help="Run in verbose mode."
        )

        args = parser.parse_args()

        if args.verbose:
            logging.basicConfig(
                format="%(asctime)s: %(levelname)s - %(message)s", level=logging.DEBUG
            )
        else:
            logging.basicConfig(
                format="%(asctime)s: %(levelname)s - %(message)s", level=logging.INFO
            )

        if args.file:
            compare_file(
                args.file, cache=args.cache, clean=args.clean, export=args.export,
            )
        elif args.link:
            compare_link(
                args.link, cache=args.cache, clean=args.clean, export=args.export,
            )
        else:
            compare_with_administration_file(
                cache=args.cache, clean=args.clean, export=args.export,
            )

