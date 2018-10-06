#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module will help us know how many from a given list are not present
into the system.

Authors:
    - @Funilrys, Nissar Chababy <contactTATAfunilrysTODTODcom>

Contributors:
    Let's contribute !

    @GitHubUsername, Name, Email (optional)
"""
# pylint: disable=bad-continuation


import argparse
from itertools import repeat
from json import decoder, dump, loads
from os import mkdir, path, remove
from os import sep as directory_separator
from re import compile as comp
from re import escape
from re import sub as substrings
from shutil import copyfileobj, rmtree
from subprocess import PIPE, Popen
from sys import stdout
from tarfile import open as tarfile_open

from colorama import Fore, Style
from colorama import init as initiate
from requests import get


class Settings:  # pylint: disable=too-few-public-methods
    """
    This class will save all data that can be called from anywhere in the code.
    """

    # This variable set the location of the info.json to get.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    info_from = "info.json"

    # This variable set the GitHub repository slug.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    github_slug = "mitchellkrogza/Ultimate.Hosts.Blacklist"
    # This variable set the GitHub repository slug.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    github_org_slug = "Ultimate-Hosts-Blacklist"

    # This variable set the name of the whitelist repository.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    whitelist_repo_name = "whitelist"

    # This variable set the github api url.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    github_api_url = "https://api.github.com"

    # This variable set the github raw url.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    github_raw_url = "https://raw.githubusercontent.com/"

    # This variable set the deploy raw url.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    deploy_raw_url = "https://hosts.ubuntu101.co.za/update_hosts.php"

    # This variable set the partially full url when attempting to get the
    # raw file.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    raw_link = github_raw_url + github_org_slug + "/%s/master/"
    raw_link_frontend = github_raw_url + github_slug + "/master/"

    # This variable the organisation url.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    github_org_url = "%s/orgs/%s" % (github_api_url, github_org_slug)

    # This variable save the list of repository.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    # Note: This variable is auto updated by Initiate()
    repositories = []

    # This variable set the repository to ignore.
    repo_to_ignore = ["repository-structure", "whitelist"]

    # This variable save the list of all domains.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    # Note: This variable is auto updated by Initiate()
    domains = []

    # This variable save the list of all ips.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    # Note: This variable is auto updated by Initiate()
    ips = []

    # This variable save the list of all whitelisted domain.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    # Note: This variable is auto updated by Initiate()
    whitelist = []

    # This variable save the list of all whitelisted domain in regex format.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    # Note: This variable is auto updated by Initiate()
    regex_whitelist = ""

    # This variable is used to set the marker that we use to say that we
    # match all occurence of the domain or IP.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    whitelist_all_marker = "ALL "

    # This variable is used to save the link to compare.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    # Note: This variable is auto updated by ARGS
    link = ""

    # This variable is used to save the file to compare.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    # Note: This variable is auto updated by ARGS
    file = ""

    # This variable set the regex to use to catch IPv4.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    regex_ip4 = r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[0-9]{1,}\/[0-9]{1,})$"  # pylint: disable=line-too-long

    # This variable set the regex to use to catch IPv4.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    regex_domain = r"^(?=.{0,253}$)(([a-z0-9][a-z0-9-]{0,61}[a-z0-9]|[a-z0-9])\.)+((?=.*[^0-9])([a-z0-9][a-z0-9-]{0,61}[a-z0-9]|[a-z0-9]))$"  # pylint: disable=line-too-long

    # This variable set the char to use when something is done.
    done = Fore.GREEN + Style.BRIGHT + "✔"

    # This variable set the char to use when an error occured
    error = Fore.RED + Style.BRIGHT + "✘"


class Initiate:
    """
    This class is used as the main entry of the script.
    Please note that this class also initiate several actions before being
    used or called.

    Argument:
        - init: bool
            If False we do not run the initiation process.
    """

    def __init__(self, init=True):
        if init:
            self.get_latest()
            self.get_whitelist()

            if not Settings.link and not Settings.file:
                data_from_info = Helpers.Dict().from_json(
                    Helpers.File(Settings.info_from).read()
                )

                if data_from_info["link"]:
                    Settings.link = data_from_info["link"]
                elif data_from_info["file"]:
                    Settings.file = data_from_info["file"]
                else:
                    raise Exception("Nothing to compare with.")

    @classmethod
    def _format_line(cls, line):
        """
        This method format a line so that we get abstraction of what is not
        a domain or IP.

        Argument:
            - line: str
                The line to format.
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

    @classmethod
    def get_latest(cls):
        """
        This method will download the latest file from upstream.
        """

        link_to_download_domains = Settings.raw_link_frontend + "domains.list.tar.gz"
        link_to_download_ips = Settings.raw_link_frontend + "ips.list.tar.gz"
        destination_domains = "domains.tar.gz"
        destination_ips = "ips.tar.gz"

        temp_dir = "temp"

        print("Download of upstream data", end=" ")

        if (
            Helpers.Download(
                link_to_download_domains, destination_domains, convert_to_idna=False
            ).link()
            and Helpers.Download(
                link_to_download_ips, destination_ips, convert_to_idna=False
            ).link()
        ):
            if not path.isdir("temp"):
                mkdir(temp_dir)

            Helpers.File(destination_domains).tar_gz_decompress(temp_dir)
            Helpers.File(destination_ips).tar_gz_decompress(temp_dir)

            Settings.domains = Helpers.File(
                temp_dir + directory_separator + "domains.list"
            ).to_list()

            Settings.ips = Helpers.File(
                temp_dir + directory_separator + "ips.list"
            ).to_list()

            Helpers.Directory(temp_dir).delete()
            Helpers.File(destination_ips).delete()
            Helpers.File(destination_domains).delete()
            print(Settings.done)
        else:
            print(Settings.error)
            raise Exception("Unable to download.")

    @classmethod
    def _whitelist_parser(cls, line):
        """
        This method will get and parse all whitelist domain into
        Settings.whitelist.

        Argument:
            - line: str
                The extracted line.
        """

        if line and not line.startswith("#"):
            if line.startswith(Settings.whitelist_all_marker):
                to_check = line.split(Settings.whitelist_all_marker)[1]
                regex_whitelist = escape(to_check) + "$"
            else:
                to_check = line
                regex_whitelist = "^%s$" % escape(line)

            if (
                Helpers.Regex(to_check, Settings.regex_ip4, return_data=False).match()
                or Helpers.Regex(
                    to_check, Settings.regex_domain, return_data=False
                ).match()
                or line.startswith(Settings.whitelist_all_marker)
            ):

                Settings.whitelist.append(regex_whitelist)

    def get_whitelist(self):
        """
        This method will get the list of whitelisted domain.
        """

        domains_url = (
            Settings.raw_link + "domains.list"
        ) % Settings.whitelist_repo_name

        req = get(domains_url)

        print("Getting %s" % Settings.whitelist_repo_name, end=" ")
        if req.status_code == 200:
            list(map(self._whitelist_parser, req.text.split("\n")))
            Settings.whitelist = Helpers.List(Settings.whitelist).format()

            Settings.regex_whitelist = "|".join(Settings.whitelist)
            print(Settings.done)
        else:
            print(Settings.error)

    def data_parser(self, line, return_data=False):
        """
        Given the extracted line, this method append the data
        to its final location.

        Arguments:
            - line: str
                The extracted line.
            - return_data: bool
                If true we return data otherwise we append to final location.
        """

        type_of_extracted = ""

        if line and not line.startswith("#"):
            line = self._format_line(line)

            if Helpers.Regex(line, Settings.regex_ip4, return_data=False).match():

                type_of_extracted = "ips"
                if not return_data:
                    Settings.ips.append(line)
            elif Helpers.Regex(line, Settings.regex_domain, return_data=False).match():
                type_of_extracted = "domains"

                if not return_data:
                    Settings.domains.append(line)

            stdout.flush()

        if return_data and type_of_extracted:
            return [line, type_of_extracted]

        if return_data:
            return "well what so say ..."

        return ""


class Compare:  # pylint: disable=too-many-instance-attributes
    """
    This class compare a list with our core list.
    """

    def __init__(self):
        if Settings.link or Settings.file:
            self.domains = []
            self.ips = []

            self.not_present_domains = 0
            self.not_present_ips = 0

            self.length_core_domains = 0
            self.length_core_ips = 0

            self.length_domains = 0
            self.length_ips = 0

            self.length_not_present_domains = 0
            self.length_not_present_ips = 0

            self.length_overall = 0
            self.length_core_overall = 0

            self.percentage_not_present_domains = 0
            self.percentage_not_present_ips = 0

            self.data_extractor()

    def calculation(self):
        """
        This method will calculate everything that is needed.
        """

        self.not_present_domains = list(set(self.domains) - set(Settings.domains))
        self.not_present_ips = list(set(self.ips) - set(Settings.ips))

        self.length_core_domains = len(Settings.domains)
        self.length_core_ips = len(Settings.ips)

        self.length_domains = len(self.domains)
        self.length_ips = len(self.ips)

        self.length_not_present_domains = len(self.not_present_domains)
        self.length_not_present_ips = len(self.not_present_ips)

        self.length_overall = self.length_domains + self.length_ips
        self.length_core_overall = self.length_core_domains + self.length_core_ips

        self.percentage_not_present_domains = int(
            (self.length_not_present_domains * 100) / self.length_overall
        )
        self.percentage_not_present_ips = int(
            (self.length_not_present_ips * 100) / self.length_overall
        )

    def _filter_data(self, info):
        """
        This method assign data from Initiate()._data_parser()
        to self.domains or self.ips
        """

        if isinstance(info, list):
            current_data = getattr(self, info[1])
            current_data.append(info[0])

            setattr(self, info[1], current_data)

    def data_extractor(self):
        """
        This method extract everything from the given link.
        """

        downloaded_destination = Settings.link.split("/")[-1]
        if (
            Settings.link
            and Helpers.Download(Settings.link, downloaded_destination, True).link()
        ):
            data = Helpers.File(downloaded_destination).to_list()

            Helpers.File(downloaded_destination).delete()

        elif Settings.file:
            data = Helpers.File(Settings.file).to_list()
        else:
            raise Exception("Nothing to compare with.")

        data = Helpers.Regex(data, Settings.regex_whitelist).not_matching_list()

        parsed = list(map(Initiate(False).data_parser, data, repeat(True)))
        list(map(self._filter_data, parsed))

        self.calculation()

        print("\n")
        # pylint: disable=anomalous-backslash-in-string
        print(
            Fore.GREEN
            + """
        ###########################################################################
        #            _ _   _                 _                                    #
        #      /\ /\| | |_(_)_ __ ___   __ _| |_ ___                              #
        #     / / \ \ | __| | '_ ` _ \ / _` | __/ _ \                             #
        #     \ \_/ / | |_| | | | | | | (_| | ||  __/                             #
        #      \___/|_|\__|_|_| |_| |_|\__,_|\__\___|                             #
        #                      _           ___ _            _    _ _     _        #
        #       /\  /\___  ___| |_ ___    / __\ | __ _  ___| | _| (_)___| |_      #
        #      / /_/ / _ \/ __| __/ __|  /__\// |/ _` |/ __| |/ / | / __| __|     #
        #     / __  / (_) \__ \ |_\__ \ / \/  \ | (_| | (__|   <| | \__ \ |_      #
        #     \/ /_/ \___/|___/\__|___/ \_____/_|\__,_|\___|_|\_\_|_|___/\__|     #
        #                                                                         #
        ###########################################################################
        """
            + Fore.RESET
        )

        print("Number of entries: %d" % self.length_core_overall)
        print("Number of domains: %d" % self.length_core_domains)
        print("Number of ips: %d" % self.length_core_ips)

        print("\n")

        print(
            Fore.CYAN
            + """
        #####################################################
        #   _____          _           _     __ _     _     #
        #  /__   \___  ___| |_ ___  __| |   / /(_)___| |_   #
        #    / /\/ _ \/ __| __/ _ \/ _` |  / / | / __| __|  #
        #   / / |  __/\__ \ ||  __/ (_| | / /__| \__ \ |_   #
        #   \/   \___||___/\__\___|\__,_| \____/_|___/\__|  #
        #                                                   #
        #####################################################
        """
            + Fore.RESET
        )

        print("Number of entries: %d" % self.length_overall)
        print("Number of domains: %d" % self.length_domains)
        print(
            "Number of new domains: %d (%d%%)"
            % (self.length_not_present_domains, self.percentage_not_present_domains)
        )
        print("Number of ips: %d" % self.length_ips)
        print(
            "Number of new ips: %d (%d%%)"
            % (self.length_not_present_ips, self.percentage_not_present_ips)
        )


class Helpers:  # pylint: disable=too-few-public-methods
    """
    Well, thanks to those helpers :-)
    """

    class Download:  # pylint: disable=too-few-public-methods
        """
        This class will initiate a download of the desired link.

        Arguments:
            - link_to_download: str
                The link to the file we are going to download.
            - destination: str
                The destination of the downloaded data.
        """

        def __init__(self, link_to_download, destination, convert_to_idna=False):
            self.link_to_download = link_to_download
            self.destination = destination
            self.convert_to_idna = convert_to_idna

        def _convert_to_idna(self, data):
            """
            This method convert a given data into IDNA format.

            Argument:
                - data: str
                    The downloaded data.
            """

            if self.convert_to_idna:
                to_write = []

                for line in data.split("\n"):
                    line = line.split()
                    try:
                        if isinstance(line, list):
                            converted = []
                            for string in line:
                                converted.append(string.encode("idna").decode("utf-8"))

                            to_write.append(" ".join(converted))
                        else:
                            to_write.append(line.encode("idna").decode("utf-8"))
                    except UnicodeError:
                        if isinstance(line, list):
                            to_write.append(" ".join(line))
                        else:
                            to_write.append(line)
                return to_write

            return None

        def link(self):
            """
            This method initiate the download.
            """

            if self.link_to_download:
                request = get(self.link_to_download, stream=True)

                if request.status_code == 200:
                    if self.convert_to_idna:
                        Helpers.File(self.destination).write(
                            "\n".join(self._convert_to_idna(request.text)),
                            overwrite=True,
                        )
                    else:
                        with open(self.destination, "wb") as file:
                            request.raw.decode_content = True
                            copyfileobj(request.raw, file)

                    del request

                    return True

            return False

    class List:  # pylint: disable=too-few-public-methods
        """
        List manipulation.
        """

        def __init__(self, main_list=None):
            if main_list is None:
                self.main_list = []
            else:
                self.main_list = main_list

        def format(self):
            """
            Return a well formated list. Basicaly, it's sort a list and remove duplicate.
            """

            try:
                return sorted(list(set(self.main_list)), key=str.lower)

            except TypeError:
                return self.main_list

    class Dict:
        """
        Dictionary manipulations.

        Argument:
            - main_dictionnary: dict
                The main_dictionnary to pass to the whole class.
        """

        def __init__(self, main_dictionnary=None):

            if main_dictionnary is None:
                self.main_dictionnary = {}
            else:
                self.main_dictionnary = main_dictionnary

        def to_json(self, destination):
            """
            Save a dictionnary into a JSON file.

            Argument:
                - destination: str
                    A path to a file where we're going to Write the
                    converted dict into a JSON format.
            """

            with open(destination, "w") as file:
                dump(
                    self.main_dictionnary,
                    file,
                    ensure_ascii=False,
                    indent=4,
                    sort_keys=True,
                )

        @classmethod
        def from_json(cls, data):
            """
            Convert a JSON formated string into a dictionary.

            Argument:
                data: str
                    A JSON formeted string to convert to dict format.
            """

            try:
                return loads(data)

            except decoder.JSONDecodeError:
                return {}

    class File:  # pylint: disable=too-few-public-methods
        """
        File treatment/manipulations.

        Arguments:
            file: str
                Path to the file to manipulate.
        """

        def __init__(self, file):
            self.file = file

        def read(self):
            """
            Read a given file path and return its content.
            """

            with open(self.file, "r", encoding="utf-8") as file:
                funilrys = file.read()

            return funilrys

        def write(self, data_to_write, overwrite=False):
            """
            Write or append data into the given file path.

            :param data_to_write: A string, the data to write.
            """

            if data_to_write is not None and isinstance(data_to_write, str):
                if overwrite or not path.isfile(self.file):
                    with open(self.file, "w", encoding="utf-8") as file:
                        file.write(data_to_write)
                else:
                    with open(self.file, "a", encoding="utf-8") as file:
                        file.write(data_to_write)

        def to_list(self):
            """
            Read a file path and return each line as a list element.
            """

            result = []

            for read in open(self.file):
                result.append(read.rstrip("\n").strip())

            return result

        def tar_gz_decompress(self, destination):
            """
            Decompress a given file into the given destination.

            Argument:
                - destination: str
                    The destination of the decompressed.
            """

            if destination is not None and isinstance(destination, str):
                with tarfile_open(self.file) as thetar:
                    thetar.extractall(path=destination)

        def delete(self):
            """
            Delete a given file path.
            """

            try:
                remove(self.file)
            except OSError:
                pass

    class Directory:  # pylint: disable=too-few-public-methods
        """
        Directory treatment/manipulations.

        Argument:
            - directory: str
                A path to the directory to manipulate.
        """

        def __init__(self, directory):
            self.directory = directory

        def delete(self):
            """
            This method delete the given directory.
            """

            try:
                rmtree(self.directory)
            except FileNotFoundError:
                pass

    class Regex:  # pylint: disable=too-few-public-methods

        """A simple implementation ot the python.re package


        :param data: A string, the data to regex check
        :param regex: A string, the regex to match
        :param return_data: A boolean, if True, return the matched string
        :param group: A integer, the group to return
        :param rematch: A boolean, if True, return the matched groups into a
            formated list. (implementation of Bash ${BASH_REMATCH})
        :param replace_with: A string, the value to replace the matched regex with.
        :param occurences: A int, the number of occurence to replace.
        """

        def __init__(self, data, regex, **args):
            # We initiate the needed variable in order to be usable all over
            # class
            self.data = data

            # We assign the default value of our optional arguments
            optional_arguments = {
                "escape": False,
                "group": 0,
                "occurences": 0,
                "rematch": False,
                "replace_with": None,
                "return_data": True,
            }

            # We initiate our optional_arguments in order to be usable all over the
            # class
            for (arg, default) in optional_arguments.items():
                setattr(self, arg, args.get(arg, default))

            if self.escape:  # pylint: disable=no-member
                self.regex = escape(regex)
            else:
                self.regex = regex

        def match(self):
            """Used to get exploitable result of re.search"""

            # We initate this variable which gonna contain the returned data
            result = []

            # We compile the regex string
            to_match = comp(self.regex)

            # In case we have to use the implementation of ${BASH_REMATCH} we use
            # re.findall otherwise, we use re.search
            if self.rematch:  # pylint: disable=no-member
                pre_result = to_match.findall(self.data)
            else:
                pre_result = to_match.search(self.data)

            if self.return_data and pre_result is not None:  # pylint: disable=no-member
                if self.rematch:  # pylint: disable=no-member
                    for data in pre_result:
                        if isinstance(data, tuple):
                            result.extend(list(data))
                        else:
                            result.append(data)

                    if self.group != 0:  # pylint: disable=no-member
                        return result[self.group]  # pylint: disable=no-member

                else:
                    result = pre_result.group(
                        self.group  # pylint: disable=no-member
                    ).strip()

                return result

            elif (
                not self.return_data  # pylint: disable=no-member
                and pre_result is not None
            ):
                return True

            return False

        def not_matching_list(self):
            """
            This method return a list of string which don't match the
            given regex.
            """

            pre_result = comp(self.regex)

            return list(
                filter(lambda element: not pre_result.search(element), self.data)
            )

        def replace(self):
            """Used to replace a matched string with another."""

            if self.replace_with is not None:  # pylint: disable=no-member
                return substrings(
                    self.regex,
                    self.replace_with,  # pylint: disable=no-member
                    self.data,
                    self.occurences,  # pylint: disable=no-member
                )

            return self.data

    class Command:
        """
        Shell command execution.

        Arguments:
            command: A string, the command to execute.
            allow_stdout: A bool, If true stdout is always printed otherwise stdout
                is passed to PIPE.
        """

        def __init__(self, command, allow_stdout=True):
            self.decode_type = "utf-8"
            self.command = command
            self.stdout = allow_stdout

        def decode_output(self, to_decode):
            """Decode the output of a shell command in order to be readable.

            Arguments:
                to_decode: byte(s), Output of a command to decode.
            """
            if to_decode is not None:
                # return to_decode.decode(self.decode_type)
                return str(to_decode, self.decode_type)

            return False

        def execute(self):
            """Execute the given command."""

            if not self.stdout:
                process = Popen(self.command, stdout=PIPE, stderr=PIPE, shell=True)
            else:
                process = Popen(self.command, stderr=PIPE, shell=True)

            (output, error) = process.communicate()

            if process.returncode != 0:
                decoded = self.decode_output(error)

                if not decoded:
                    return "Unkown error. for %s" % (self.command)

                print(decoded)
                exit(1)
            return self.decode_output(output)


if __name__ == "__main__":
    initiate(autoreset=True)

    PARSER = argparse.ArgumentParser(
        description="A script to compare a given link or file to \
        Ultimate.Hosts.Blacklist infrastructure.",
        epilog="Crafted with %s by %s"
        % (
            Fore.RED + "♥" + Fore.RESET,
            Style.BRIGHT + Fore.CYAN + "Nissar Chababy (Funilrys)",
        ),
    )

    PARSER.add_argument("-l", "--link", type=str, help="Link to compare.")
    PARSER.add_argument("-f", "--file", type=str, help="File to compare.")

    ARGS = PARSER.parse_args()

    if ARGS.link:
        Settings.link = ARGS.link
    elif ARGS.file:
        Settings.file = ARGS.file

    Initiate()
    Compare()
