"""
The helpers classes/function of the Ultimate-Hosts-Blacklist project.

Provide the helpers we use for dict manipulation.

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
from json import decoder, dump, loads

from ultimate_hosts_blacklist.helpers import List


class Dict:  # pylint: disable=too-few-public-methods, bad-continuation
    """
    Dictionary manipulations.

    :param main_dictionnary: The :code:`dict` we are working with.
    :type main_dictionnary: dict
    """

    def __init__(self, main_dictionnary=None):
        if main_dictionnary is None:
            self.main_dictionnary = {}
        else:
            self.main_dictionnary = main_dictionnary

    def to_json(self, destination):
        """
        Save a dictionnary into a JSON file and format.

        :param destination:
            A path to a file where we're going to Write the
            converted dict into a JSON format.
        :type destination: str
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
    def from_json(cls, json):
        """
        Given a JSON formatted string, we convert it
        into a dict which we return.

        :param json: A JSON formatted string.
        :type json: str
        """

        try:
            return loads(json)
        except decoder.JSONDecodeError:
            return {}

    def merge(self, to_merge, strict=True):
        """
        Merge the content of :code:`to_merge` into the main dictionnary.

        :param dict to_merge: The dictionnary to merge.

        :param bool strict:
            Tell us if we have to strictly merge lists.

            - :code:`True`: We follow index.
            - :code:`False`: We follow element (content/value)

        :return: The merged dict.
        :rtype: dict
        """

        # We initiate a variable which will save our result.
        result = {}

        for index, data in to_merge.items():
            # We loop through the given dict to merge.

            if index in self.main_dictionnary:
                # The currently read index is in the main dict.

                if isinstance(data, dict) and isinstance(
                    self.main_dictionnary[index], dict
                ):
                    # They are dict in both sides.

                    # We merge the dict tree and save into the local result.
                    result[index] = Dict(self.main_dictionnary[index]).merge(
                        data, strict=strict
                    )
                elif isinstance(data, list) and isinstance(
                    self.main_dictionnary[index], list
                ):
                    # They are list in both sides.

                    # We merge the lists and save into the local result.
                    result[index] = List(self.main_dictionnary[index]).merge(
                        data, strict=strict
                    )
                else:
                    # They are not list nor dict.

                    result[index] = data
            else:
                # The currently read index is not in the main dict.

                # We create it.
                result[index] = data

        for index, data in self.main_dictionnary.items():
            # We loop through each element of the main dict.

            if index not in result:
                # The currently read index is not into
                # the result.

                # We append it to the result.
                result[index] = data

        # We return the result.
        return result
