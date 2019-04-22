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
# pylint: disable=bad-continuation
from os import walk
from tempfile import gettempdir

from domain2idna import get as domain2idna

from ultimate_hosts_blacklist.helpers import Directory, Download, File, List
from ultimate_hosts_blacklist.input_repo_updater.configuration import (
    Outputs,
    directory_separator,
)
from ultimate_hosts_blacklist.input_repo_updater.our_pyfunceble import OurPyFunceble


class DomainsList:
    """
    Get, format and save the upstream source into `domains.list`.
    """

    # Save the raw link we have to download.
    raw_link = None
    # Save the content of the upstream (raw link).
    upstream = None

    def __init__(self, raw_link):
        # We share the raw link.
        self.raw_link = raw_link

        # We create a local instance of PyFunceble.
        self.our_pyfunceble = OurPyFunceble()

        File(Outputs.input_destination).write(self.format(self.get()), overwrite=True)

    def __get_from_tar_gz(self):
        """
        Download the tar.gz and compile all files into the result.
        """

        # We construct the path to the temp directory.
        our_tempdir = "{0}{1}ultimate-input_source{1}".format(
            gettempdir(), directory_separator
        )
        # We construct the path to the decompression directory.
        decompression_dir = "{0}upstream".format(our_tempdir)

        # We create the temporary directory.
        Directory(our_tempdir).create()

        # We construct the final file.
        destination = "{0}upstream_file".format(our_tempdir)

        if not Download(self.raw_link, destination).link():
            # We could not download the raw link.

            # We raise an exception, we can't do nothing without something
            # to test.
            raise Exception("Unable to download {0}.".format(repr(self.raw_link)))

        # We decompress the file into the decompression directory.
        File(destination).tar_gz_decompress(decompression_dir)

        # We initiate the variable which will save the output.
        result = []

        for root, _, files in walk(decompression_dir):
            # We loop through all files in all directory
            # into the decompressed directory.

            for file in files:
                # We loop through the list of found file.

                # We append the content of the currently
                # read filename into the result.
                result.append(
                    File("{0}{1}{2}".format(root, directory_separator, file)).read()
                )

        # We finally delete the decompression directory.
        Directory(decompression_dir).delete()
        # And the compressed file.
        File(destination).delete()

        # And the return the result as a big string.
        return "\n".join(result)

    def get(self):
        """
        Get the upstream version.
        """

        if self.raw_link:
            # The raw link is given.

            if self.raw_link.endswith(".tar.gz"):
                # The raw link is a tarball.

                # We get and return the compilation of each
                # files of the tarball.
                return self.__get_from_tar_gz()

            # We download the content of the raw link.
            upstream = Download(self.raw_link, None).link()

            if isinstance(upstream, str):
                # The downloaded data is a str.

                # We return the upstream content.
                return upstream

            # Otherwise, we raise an exception, we can't do nothing without
            # something to test.
            raise Exception(
                "Unable to get the content of {0}.".format(repr(self.raw_link))
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

    def format(self, data):
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

        # We initiate what will save our result.
        result = []

        for line in data:
            # We loop through each lines.
            line = line.strip()

            if not line:
                # The line is empty.

                # We continue the loop.
                continue

            if line.startswith("#"):
                # The line is a comment line.

                # We continue the loop.
                continue

            # We format the line and conver to idna.
            line = domain2idna(self.__extract_domains_from_line(line))

            if line.startswith("www.") and line[4:] not in result:
                # * The line starts with `www.`
                # and
                # * The line without `www.` is not listed.

                # We append the line without`www.` to the list to test.
                result.append(line[4:])
            elif self.our_pyfunceble.pyfunceble.is_domain(  # pylint: disable=no-member
                line
            ) and not self.our_pyfunceble.pyfunceble.is_subdomain(  # pylint: disable=no-member
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

        return "\n".join(List(result).format(delete_empty=True))
