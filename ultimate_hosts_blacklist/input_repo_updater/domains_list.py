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
from os import path, makedirs, walk
from tempfile import tempdir
from ultimate_hosts_blacklist.input_repo_updater.configuration import (
    directory_separator,
)
from ultimate_hosts_blacklist.helpers import File, Download, Directory


class DomainsList:
    """
    Get, format and save the upstream source into `domains.list`.
    """

    raw_link = None
    upstream = None

    def __init__(self, raw_link):
        self.raw_link = raw_link

    def __get_from_tar_gz(self):
        """
        Download the tar.gz and compile all files into the result.
        """

        our_tempdir = "{0}{1}ultimate-input_source{1}".format(
            tempdir, directory_separator
        )
        decompression_dir = "{0}upstream".format(our_tempdir)

        if not path.isdir(our_tempdir):
            makedirs(our_tempdir)

        destination = "{0}{1}".format(our_tempdir, directory_separator)

        if not Download(self.raw_link, destination).link():
            raise Exception("Unable to download {0}.".format(repr(self.raw_link)))

        File(destination).tar_gz_decompress(decompression_dir)

        result = []

        for root, _, files in walk(decompression_dir):
            for file in files:
                with open(file, "r", encoding="utf-8") as file_stream:
                    result.append(file_stream.read())

        Directory(decompression_dir).delete()
        File(destination).delete()

        return "\n".join(result)


    def get(self):
        """
        Get the upstream version.
        """

        if self.raw_link:
            if self.raw_link.endswith(".tar.gz"):
                return self.__get_from_tar_gz()

