"""
The tool to update the input repositories of the Ultimate-Hosts-Blacklist project.

Provide an interface to get or edit the administration file.

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

from ultimate_hosts_blacklist.input_repo_updater import logging
from ultimate_hosts_blacklist.input_repo_updater.configuration import Infrastructure
from ultimate_hosts_blacklist.helpers import File, Dict, Command


class Administration:
    """
    Provide the information of the administration file.
    """

    location = Infrastructure.administration_file
    data = {}

    def __init__(self):
        self.data.update(self.get())

    def __convert_into_understandable(self, data):
        """
        Convert the given data values into something we understand.
        """

        result = {}

        for index, value in data.items():
            if index in Infrastructure.unneeded_indexes:
                continue
            elif index == "name":
                result[index] = Command("basename `git rev-parse --show-toplevel`", allow_stdout=False).execute().strip()
            elif index in Infrastructure.should_be_bool:
                result[index] = bool(int(value))
            elif index in Infrastructure.should_be_int:
                result[index] = int(value)
            else:
                result[index] = value

        return result

    def get(self):
        """
        Read and return the content of teh administration file.
        """

        content = File(self.location).read()
        logging.debug("Administration file content: \n{0}".format(content))

        data = Dict.from_json(content)

        return self.__convert_into_understandable(data)

    def save(self, data=None):
        """
        Save the current state of the administration file.
        """

        if data is None:
            data = self.data

        Dict(data).to_json(self.location)
