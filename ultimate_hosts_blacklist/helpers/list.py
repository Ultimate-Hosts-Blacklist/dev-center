"""
The helpers classes/function of the Ultimate-Hosts-Blacklist project.

Provide the helpers we use for list manipulation.

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


class List:  # pylint: disable=too-few-public-methods, bad-continuation
    """
    List manipulation.

    :param main_list: The list we are working with.
    :type main_list: list
    """

    def __init__(self, main_list=None):
        if main_list is None:  # pragma: no cover
            self.main_list = []
        else:
            self.main_list = main_list

    def format(self, delete_empty=False):
        """
        Return a well formated list. Basicaly, it's sort a list and remove duplicate.

        :param delete_empty: Tell us if we have to remove all empty element of the list.
        :type delte_empty: bool
        """

        try:
            formatted = sorted(list(set(self.main_list)), key=str.lower)

            if delete_empty and formatted and not formatted[0]:
                return formatted[1:]
            return formatted
        except TypeError:  # pragma: no cover
            return self.main_list

    def delete_none_element(self):
        """
        Delete all None type elements.
        """

        return [x for x in self.main_list if x]

    def merge(self, to_merge, strict=True):
        """
        Merge to_merge into the given main list.

        :param list to_merge: The list to merge.

        :param bool strict:
            Tell us if we have to respect index (:code:`True`)
            or not (:code:`False`).

        :return: The merged list.
        :rtype: list
        """

        from ultimate_hosts_blacklist.helpers.dict import Dict

        # We initiate a variable which will save the
        # result
        result = []

        if strict:
            # We are in strict mode.

            for index, element in enumerate(to_merge):
                # We loop through each element of the list to merge
                # to the main dict.

                try:
                    if isinstance(element, dict) and isinstance(
                        self.main_list[index], dict
                    ):
                        # The currently read element is a dict.

                        # We merge its content into the main dict
                        # and append into the result.
                        result.append(Dict(self.main_list[index]).merge(element))
                    elif isinstance(element, list) and isinstance(
                        self.main_list[index], list
                    ):
                        # The currently read element is a list.

                        # We loop through this method.
                        result.append(List(self.main_list[index]).merge(element))
                    else:
                        # The currently read element is not a list
                        # nor a dict.

                        # We append the element to the result.
                        result.append(element)
                except IndexError:  # pragma: no cover
                    # The index does not exist.
                    # Which means that for example one list is bigger
                    # than the other one.

                    # We append the element to the result.
                    result.append(element)
        else:
            # We are not is strict mode.

            # We initiate the result with the main list.
            result = self.main_list

            for element in to_merge:
                # We loop through the element to merge.

                if element not in result:
                    # The currently read element is not
                    # in the result.

                    # We append it to the result
                    result.append(element)

        # We return the result.
        return result
