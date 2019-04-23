"""
The tool to update the input repositories of the Ultimate-Hosts-Blacklist project.

Get, format and save the upstream source.
It basically construct the `domains.list´ file.

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
# pylint: disable=bad-continuation, logging-format-interpolation
import logging
from multiprocessing import Pool
from os import walk
from tempfile import gettempdir

from domain2idna import get as domain2idna

from ultimate_hosts_blacklist.helpers import Directory, Download, File, List
from ultimate_hosts_blacklist.input_repo_updater.configuration import (
    Outputs,
    directory_separator,
)


class DomainsList:
    """
    Get, format and save the upstream source into `domains.list`.
    """

    # Save the raw link we have to download.
    raw_link = None
    # Save the content of the upstream (raw link).
    upstream = None
    # Save the pyfunceble instance
    shared_pyfunceble = None

    @classmethod
    def __init__(cls, raw_link, shared_pyfunceble=None):
        # We share the raw link.
        cls.raw_link = raw_link

        # We create a local instance of PyFunceble.
        cls.shared_pyfunceble = shared_pyfunceble

        File(Outputs.input_destination).write(cls.format(cls.get()), overwrite=True)

    @classmethod
    def __get_from_tar_gz(cls):
        """
        Download the tar.gz and compile all files into the result.
        """

        # We construct the path to the temp directory.
        our_tempdir = "{0}{1}ultimate-input_source{1}".format(
            gettempdir(), directory_separator
        )
        # We construct the path to the decompression directory.
        decompression_dir = "{0}upstream-decompressed".format(our_tempdir)

        # We create the temporary directory.
        Directory(our_tempdir).create()
        # We create the decompression directory.
        Directory(decompression_dir).create()

        # We construct the final file.
        destination = "{0}{1}".format(our_tempdir, cls.raw_link.split("/")[-1])

        if not Download(cls.raw_link, destination).stream():
            # We could not download the raw link.

            # We raise an exception, we can't do nothing without something
            # to test.
            raise Exception("Unable to download {0}.".format(repr(cls.raw_link)))

        # We decompress the file into the decompression directory.
        File(destination).tar_gz_decompress(decompression_dir)

        # We update the permissions af all directories and files.
        cls.shared_pyfunceble.travis.permissions()

        # We initiate the variable which will save the output.
        result = []

        for root, _, files in walk(decompression_dir):
            # We loop through all files in all directory
            # into the decompressed directory.

            for file in files:
                # We loop through the list of found file.

                if "BL" in root and not file.endswith("domains"):
                    continue

                logging.info(
                    "Parsing {0}".format(repr(root + directory_separator + file))
                )

                try:
                    # We append the content of the currently
                    # read filename into the result.
                    result.append(
                        File("{0}{1}{2}".format(root, directory_separator, file))
                        .read_bytes()
                        .decode("utf-8")
                    )
                except UnicodeDecodeError:
                    result.append(
                        File("{0}{1}{2}".format(root, directory_separator, file))
                        .read_bytes()
                        .decode("latin-1")
                    )

        # We finally delete the decompression directory.
        Directory(decompression_dir).delete()
        # And the compressed file.
        File(destination).delete()

        # And the return the result as a big string.
        return "\n".join(result)

    @classmethod
    def get(cls):
        """
        Get the upstream version.
        """

        if cls.raw_link:
            # The raw link is given.

            if cls.raw_link.endswith(".tar.gz"):
                # The raw link is a tarball.

                # We get and return the compilation of each
                # files of the tarball.
                return cls.__get_from_tar_gz()

            # We download the content of the raw link.
            upstream = Download(cls.raw_link, None).text()

            if isinstance(upstream, str):
                # The downloaded data is a str.

                # We return the upstream content.
                return upstream

            # Otherwise, we raise an exception, we can't do nothing without
            # something to test.
            raise Exception(
                "Unable to get the content of {0}.".format(repr(cls.raw_link))
            )

        # We create an instance of the input destination file.
        file = File(Outputs.input_destination)

        if file.exists():
            # The input file exists.

            # We return its content.
            return file.read()

        # We return an empty string, we have nothing more to say :-)
        return ""

    @classmethod
    def __extract_domains_from_line(cls, line):
        """
        Given a line, we return the domains.

        :param str line: The line to format.

        :return: The partially formatted line.
        :rtype: str
        """

        if "#" in line:
            # A comment is present into the line.

            # We remove the comment..
            line = line[: line.find("#")].strip()

        if " " in line or "\t" in line:
            # * A space is present into the line.
            # or
            # * A tabs is present into the line.

            # We split every whitespace.
            splited = line.split()

            for element in splited[1:]:
                # We loop through the list of subject starting from the second element (index 1).

                if element:
                    # It is a non empty subject.

                    # We keep the currenlty read element.
                    line = element

                    # And we break the loop, there is nothing more
                    # to look for.
                    break

        return line

    @classmethod
    def get_subjects_from_line(cls, line):
        """
        Return the list of subjects to test from the
        given line.
        """

        logging.debug("Getting subjects from {0}".format(repr(line)))

        result = []

        # We loop through each lines.
        line = line.strip()

        if line and not line.startswith("#"):
            # We format the line and conver to idna.
            line = domain2idna(cls.__extract_domains_from_line(line))

            if line.startswith("www.") and line[4:] not in result:
                # * The line starts with `www.`
                # and
                # * The line without `www.` is not listed.

                # We append the line without`www.` to the list to test.
                result.append(line[4:])
            elif cls.shared_pyfunceble.pyfunceble.is_domain(  # pylint: disable=no-member
                line
            ) and not cls.shared_pyfunceble.pyfunceble.is_subdomain(  # pylint: disable=no-member
                line
            ):
                # * The line is a domain.
                # and
                # * The line is not a subdomain.

                if "www.{0}".format(line) not in result:
                    # The line with `www.` is not listed.

                    # We append the line with `www.` to the list to test.
                    result.append("www.{0}".format(line))

            # We append the formatted line to the result.
            result.append(line)

        logging.debug("Subjects: {0}".format(result))
        return result

    @classmethod
    def format(cls, data):
        """
        Given a string (whole file content) or a list (file content in list format).
        we format each lines.

        :param str data: The content we are going to test.

        :return: The data to write into the file we are going to test.
        :rtype: str
        """

        if isinstance(data, str):
            # A string is given.

            # We split every new line char.
            data = data.split("\n")
        elif not isinstance(data, list):
            # A non list is given.

            # We raise an exception, we only support str and list.
            raise ValueError(
                "{0} or {1} expected. {2} given.".format(
                    type(str), type(list), type(data)
                )
            )

        with Pool(60) as pool:
            result = [y for x in pool.map(cls.get_subjects_from_line, data) for y in x]

        return "\n".join(List(result).format(delete_empty=True))
