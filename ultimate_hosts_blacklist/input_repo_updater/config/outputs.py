"""
The tool to update the input repositories of the Ultimate-Hosts-Blacklist project.

Provides the outputs locations.

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

from os import getcwd
from os import sep as directory_separator


class Outputs:  # pylint: disable=too-few-public-methods
    """
    Provide the outputs configuration.
    """

    # The current directory path.
    current_directory = getcwd() + directory_separator

    # The name of the input file.
    input_filename = "domains.list"
    # The name of the clean list.
    clean_filename = "clean.list"
    # The name of the whitelisted list.
    whitelisted_filename = "whitelisted.list"
    # The name of the volatile list.
    volatile_filename = "volatile.list"
    # The name of the ips list.
    ip_filename = "ip.list"
    # The name of the continue file.
    continue_filename = "continue.json"
    # The name of the administration file.
    administration_filename = "info.json"
    # The name of the travis configuration file.
    travis_filename = ".travis.yml"
    # The name of the central admin file.
    central_admin_filename = ".admin"

    # The location of the input file.
    input_destination = f"{current_directory}{input_filename}"

    # The location of the clean file.
    clean_destination = f"{current_directory}{clean_filename}"

    # The location of the whitelisted file.
    whitelisted_destination = f"{current_directory}{whitelisted_filename}"

    # The location of the volatile file.
    volatile_destination = f"{current_directory}{volatile_filename}"

    # The location of the ip file.
    ip_destination = f"{current_directory}{ip_filename}"

    # The output location.
    output_destination = f"{current_directory}output{directory_separator}"

    # The location of the temporary volatile file.
    temp_volatile_destination = (
        f"{output_destination}{directory_separator}{volatile_filename}"
    )

    # The location of the continue file.
    continue_destination = (
        f"{output_destination}{directory_separator}{continue_filename}"
    )

    # The location of the list of ACTIVE domains.
    active_subjects_destination = f"{output_destination}{directory_separator}domains{directory_separator}ACTIVE{directory_separator}list"  # pylint: disable=line-too-long

    # The location of the IP list.
    ip_subjects_destination = f"{output_destination}{directory_separator}hosts{directory_separator}ACTIVE{directory_separator}ips"  # pylint: disable=line-too-long

    # The location of the administration file.
    admin_destination = f"{current_directory}{administration_filename}"

    # The location of the travis configuration file.
    travis_destination = f"{current_directory}{travis_filename}"

    # The location of the central marker.
    central_destination = f"{current_directory}{central_admin_filename}"
