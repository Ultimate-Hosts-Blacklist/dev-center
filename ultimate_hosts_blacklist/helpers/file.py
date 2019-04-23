"""
The helpers classes/function of the Ultimate-Hosts-Blacklist project.

Provide the helpers we manipulate files.

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

from os import path, remove
from tarfile import open as tarfile_open


class File:  # pylint: disable=too-few-public-methods  # pragma: no cover
    """
    File manipulations.

    :param file: A path to the file we are working with.
    :type file: str
    """

    def __init__(self, file):
        self.file = file

    def exists(self):
        """
        Check if the given file exists.
        """

        return path.isfile(self.file)

    def read(self):
        """
        Read a given file path and return its content.
        """

        with open(self.file, "r", encoding="utf-8") as file:
            funilrys = file.read()

        return funilrys

    def read_bytes(self):
        """
        Read a given file in bytes mode and return its
        content.
        """

        with open(self.file, "rb") as file:
            funilrys = file.read()

        return funilrys

    def to_list(self):
        """
        Read a file path and return each line as a list element.
        """

        result = []

        with open(self.file, "r", encoding="utf-8") as file:
            result = file.read().splitlines()

        return result

    def write(self, data_to_write, overwrite=False):
        """
        Write or append data into the given file path.

        :param data_to_write: The data to write into the file.
        :type data_to_write: str

        :param overwrite: Overwrite.
        :type oberwrite: bool
        """

        if data_to_write is not None and isinstance(data_to_write, str):
            if overwrite or not self.exists():
                with open(self.file, "w", encoding="utf-8") as file:
                    file.write(data_to_write)
            else:
                with open(self.file, "a", encoding="utf-8") as file:
                    file.write(data_to_write)

    def delete(self):
        """
        Delete a given file path.
        """

        try:
            remove(self.file)
        except OSError:
            pass

    def tar_gz_decompress(self, destination):
        """
        Decompress the given file into the given destination.

        :param str destination: The destination of the decompression.
        """

        if destination is not None and isinstance(destination, str):
            with tarfile_open(self.file) as thetar:
                thetar.extractall(path=destination)
        else:
            raise ValueError(
                "{0} expected. {1} given.".format(type(str), type(destination))
            )
