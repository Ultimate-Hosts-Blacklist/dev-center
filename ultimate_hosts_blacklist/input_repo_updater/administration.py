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

from ultimate_hosts_blacklist.helpers import Command, Dict, File
from ultimate_hosts_blacklist.input_repo_updater import logging
from ultimate_hosts_blacklist.input_repo_updater.configuration import Infrastructure


class Administration:
    """
    Provide the information of the administration file.
    """

    # This is the location of the administration file.
    location = File(Infrastructure.administration_file)
    # Saves the administration file.
    data = {}

    def __init__(self):
        self.data.update(self.get())

    @classmethod
    def __convert_into_understandable(cls, data):
        """
        Convert the given data values into something we understand.

        :param dict data: The content of the administration file.

        :return: The understandable data.
        :rtype: dict
        """

        # We initiate a variable which will save the final
        # output.
        result = {}

        for index, value in data.items():
            # We loop through the keys and values
            # of the given data.

            if index in Infrastructure.unneeded_indexes:
                # The currenctly needed index is not needed.

                # We continue the loop.
                continue
            elif index == "name":
                # The index is the name.

                # We get/set the name from the repository name.
                result[index] = (
                    Command(
                        "basename `git rev-parse --show-toplevel`", allow_stdout=False
                    )
                    .execute()
                    .strip()
                )
            elif index in Infrastructure.should_be_bool:
                # The index is in the list of indexes
                # which should be bool interpretted.

                # We convert the value to bool and append
                # the result into the result.
                result[index] = bool(int(value))
            elif index in Infrastructure.should_be_int:
                # The index is in the list of indexes
                # which should be int interpretted.

                # We conver the value to int and append
                # the result into the result.
                result[index] = int(value)
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

        # We initiate a variable which will save the final
        # output.
        result = {}
        for index, value in data.items():
            # We loop through the keys and values
            # of the given data.

            if index in Infrastructure.unneeded_indexes:
                # The currenctly needed index is not needed.

                # We continue.
                continue
            elif index in Infrastructure.should_be_bool:
                # The index is in the list of indexes
                # which should be bool interpretted.

                # We convert the value to bool then to str and append
                # the result into the result.
                result[index] = str(int(bool(value)))
            elif index in Infrastructure.should_be_int:
                # The index is in the list of indexes
                # which should be int interpretted.

                # We conver the value to int and append
                # the result into the result.
                result[index] = int(value)
            else:
                result[index] = value

        return result

    def get(self):
        """
        Read and return the content of teh administration file.
        """

        # We get the content of the administration file.
        content = self.location.read()
        logging.debug("Administration file content: \n{0}".format(content))

        # We convert it to a dict.
        data = Dict.from_json(content)

        # And we return the understable version of it.
        return self.__convert_into_understandable(data)

    def save(self, data=None):
        """
        Save the current state of the administration file.
        """

        if data is None:
            data = self.data

        Dict(self.__convert_into_not_understandable(data)).to_json(self.location.file)
