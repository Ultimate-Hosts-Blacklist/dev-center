"""
The helpers classes/function of the Ultimate-Hosts-Blacklist project.

Provide the helpers we use for regex match.

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

from re import compile as comp


class Regex:  # pylint: disable=too-few-public-methods

    """A simple implementation ot the python.re package

    :param data: The data we are working with:
    :type data: str

    :param regex: The regex to match.
    :type regex: str|regex

    :param group: The group to return.
    :type group: int

    :param return_data:
        Tell us if we only match and return the matching state.
        Or if we return the matched element(s).
    :param return_data: bool
    """

    def __init__(self, data, regex, **args):
        # We initiate the needed variable in order to be usable all over
        # class
        self.data = data

        # We assign the default value of our optional arguments
        optional_arguments = {"group": 0, "return_data": True}

        # We initiate our optional_arguments in order to be usable all over the
        # class
        for (arg, default) in optional_arguments.items():
            setattr(self, arg, args.get(arg, default))

            self.regex = regex

    def match(self):
        """
        Used to get exploitable result of re.search
        """

        # We compile the regex string
        to_match = comp(self.regex)

        # In case we have to use the implementation of ${BASH_REMATCH} we use
        # re.findall otherwise, we use re.search
        pre_result = to_match.search(self.data)

        if self.return_data and pre_result:  # pylint: disable=no-member
            return pre_result.group(self.group).strip()  # pylint: disable=no-member

        if not self.return_data and pre_result:  # pylint: disable=no-member
            return True

        return False

    def not_matching_list(self):
        """
        This method return a list of string which don't match the
        given regex.
        """

        pre_result = comp(self.regex)

        return list(
            filter(lambda element: not pre_result.search(str(element)), self.data)
        )
