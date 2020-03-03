"""
The tool to update the input repositories of the Ultimate-Hosts-Blacklist project.

Provides an interface to get or edit the administration file.

License:
::


    MIT License

    Copyright (c) 2019, 2020  Ultimate-Hosts-Blacklist
    Copyright (c) 2019, 2020  Nissar Chababy
    Copyright (c) 2019, 2020  Mitchell Krog

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

import logging
from datetime import datetime

from PyFunceble.helpers import Dict, File

from ultimate_hosts_blacklist.helpers import Command

from .config import Infrastructure, Outputs


class Administration:
    """
    Provide the information of the administration file.
    """

    location = File(Outputs.admin_destination)
    data = {}

    def __init__(self):
        self.data.update(self.__get_them_all())

    def __contains__(self, item):
        return item in self.data

    def __getitem__(self, name):
        if name in self.data:
            return self.data[name]

        return None

    def __getattr__(self, name):
        if name in self.data:
            return self.data[name]

        raise AttributeError(name)

    def __setattr__(self, name, value):
        self.data[name] = value

    def __delattr__(self, name):
        if name in self.data:
            del self.data[name]

    @classmethod
    def __convert_into_understandable(cls, data):
        """
        Convert the given data values into something we understand.

        :param dict data: The content of the administration file.

        :return: The understandable data.
        :rtype: dict
        """

        result = {}

        for index, value in data.items():
            if index in Infrastructure.unneeded_indexes:
                continue

            if index == "name":
                result[index] = (
                    Command(
                        "basename `git rev-parse --show-toplevel`", allow_stdout=False
                    )
                    .execute()
                    .strip()
                )
            elif index in Infrastructure.should_be_bool:
                result[index] = bool(int(value))
            elif index in Infrastructure.should_be_int:
                result[index] = int(value)
            elif index in Infrastructure.should_be_dict:
                result[index] = dict(value)
            elif index in Infrastructure.should_be_datetime:
                try:
                    result[index] = datetime.fromisoformat(value)
                except ValueError:
                    result[index] = datetime.now()
            elif index in Infrastructure.should_be_epoch_datetime:
                result[index] = datetime.fromtimestamp(value)
            else:
                result[index] = value

        return result

    @classmethod
    def __convert_into_not_understandable(cls, data):
        """
        Convert the given values into something we don't understand.

        :param dict data: The content of the administration file.

        :return: The not understandable data.
        :rtype: dict
        """

        result = {}
        for index, value in data.items():
            if index in Infrastructure.unneeded_indexes:
                continue

            if index in Infrastructure.should_be_bool:
                result[index] = bool(value)
            elif index in Infrastructure.should_be_int:
                result[index] = int(value)
            elif index in Infrastructure.should_be_datetime:
                result[index] = value.isoformat()
            elif index in Infrastructure.should_be_epoch_datetime:
                result[index] = value.timestamp()
            else:
                result[index] = value

        return result

    def __get_them_all(self):
        """
        Read and return the content of teh administration file.
        """

        content = self.location.read()
        logging.debug("Administration file content: \n%s", content)

        data = Dict.from_json(content)

        return self.__convert_into_understandable(data)

    def save(self, data=None):
        """
        Save the current state of the administration file.
        """

        if data is None:
            data = self.data

        Dict(self.__convert_into_not_understandable(data)).to_json_file(
            self.location.path
        )
