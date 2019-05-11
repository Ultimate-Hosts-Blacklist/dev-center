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

from yaml import dump as yaml_dump
from yaml import safe_load as yaml_load


class Dict:  # pylint: disable=too-few-public-methods, bad-continuation
    """
    Dictionary manipulations.

    :param main: The :code:`dict` we are working with.
    :type main: dict
    """

    def __init__(self, main=None):
        if main is None:
            self.main = {}
        else:
            self.main = main

    def to_json(self, destination):
        """
        Save a dictionnary into a JSON file and format.

        :param destination:
            A path to a file where we're going to Write the
            converted dict into a JSON format.
        :type destination: str
        """

        with open(destination, "w") as file:
            dump(self.main, file, ensure_ascii=False, indent=4, sort_keys=True)

    def to_yaml(self, destination, flow_style=False):
        """
        Save a dictionnary into a YAML file.

        :param str destination:
            A path to a file where we're going to write the
            converted dict into a JSON format.
        """

        with open(destination, "w") as file:
            yaml_dump(
                self.main,
                file,
                encoding="utf-8",
                allow_unicode=True,
                indent=4,
                default_flow_style=flow_style,
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

    @classmethod
    def from_yaml(cls, yaml):
        """
        Given a YAML formatted string, we convert it
        into a dict which we return.

        :param json: A YAML formatted string.
        :type json: str
        """

        return yaml_load(yaml)

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

        from ultimate_hosts_blacklist.helpers.list import List

        # We initiate a variable which will save our result.
        result = {}

        for index, data in to_merge.items():
            # We loop through the given dict to merge.

            if index in self.main:
                # The currently read index is in the main dict.

                if isinstance(data, dict) and isinstance(self.main[index], dict):
                    # They are dict in both sides.

                    # We merge the dict tree and save into the local result.
                    result[index] = Dict(self.main[index]).merge(data, strict=strict)
                elif isinstance(data, list) and isinstance(self.main[index], list):
                    # They are list in both sides.

                    # We merge the lists and save into the local result.
                    result[index] = List(self.main[index]).merge(data, strict=strict)
                else:
                    # They are not list nor dict.

                    result[index] = data
            else:
                # The currently read index is not in the main dict.

                # We create it.
                result[index] = data

        for index, data in self.main.items():
            # We loop through each element of the main dict.

            if index not in result:
                # The currently read index is not into
                # the result.

                # We append it to the result.
                result[index] = data

        # We return the result.
        return result

    def flatten(self, seperator=".", previous=None):
        """
        Flatten the given dict.

        :param str separator: A separator to apply between each keys.
        :param str previous:
            DO NOT USE, used to recursively get the key of the previously set keys.
        """

        # We create a variable which will save the result.
        result = {}

        if isinstance(self.main, dict):
            # The main data is a dict.

            for key, value in self.main.items():
                # We loop through each keys and values.

                for yek, eulav in (
                    Dict(value).flatten(seperator=seperator, previous=key).items()
                ):
                    # We then loop through the flatten version of each subkeys and values.

                    if previous:
                        # The previous key was set.

                        # We initiate the flatten key with the currently read value.
                        result[previous + seperator + yek] = eulav
                    else:
                        # The previous key was not set.

                        # We initiate the flatten key the currently read key and value.
                        result[yek] = eulav
        else:
            # The main data is not a dict.

            if previous:
                # The previous key was set.

                # We use the previous key as a the key of the currently given data.
                result[previous] = self.main
            else:
                # The previous key was not set.

                while seperator in result:
                    # We loop until we are sure that the separator is not preset
                    # into the result as a key.

                    # We append the separator to the separato
                    seperator += seperator

                # We set the constructed separator as the key o f the currently given
                # data.
                result[seperator] = self.main

        # We finally return the result.
        return result

    def unflatten(self, seperator="."):
        """
        Unflatten the given flatten dict.

        :param str separator: A separator to apply between each keys.
        """

        # We create a variable which will save the result.
        result = {}

        for key, value in self.main.items():
            # We loop through each flatten keys and their values.

            # We set the context we are going to work with.
            local_result = result

            if seperator in key:
                # The separator is in the currently read key.

                for k in key.split(seperator)[:-1]:
                    # We split over the single keys (except the last one.)
                    # and we iterate over them.

                    if k not in local_result:
                        # The currently read single key is not into the
                        # current local result.

                        # We initiate it.
                        local_result[k] = {}

                    # We then update the context we are working with.
                    local_result = local_result[k]

                # We then set the value of the last key.
                local_result[key.split(seperator)[-1]] = value
            else:
                # The separator is not in the currently read key.

                # We explicitly set the currently read key and value
                # into the current local result.
                local_result[key] = value

        return result
