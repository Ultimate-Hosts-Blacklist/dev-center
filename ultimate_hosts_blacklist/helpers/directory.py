"""
The helpers classes/function of the Ultimate-Hosts-Blacklist project.

Provide the helpers we manipulate directories.

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

from os import makedirs, path
from shutil import rmtree


class Directory:
    """
    Directory manipulation.

    :param directory: A path to the directory we are working with.
    :type directory: str
    """

    def __init__(self, directory):
        self.dir = directory

    def exists(self):
        """
        Check if the given directory exists.
        """

        return path.isdir(self.dir)

    def create(self):
        """
        Create the given directory if it does not exits.
        """

        if not self.exists():
            makedirs(self.dir)

    def delete(self):
        """
        Delete the given directory if it exists.
        """

        if self.exists():
            rmtree(self.dir)
