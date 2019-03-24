"""
The tool to update the input repositories of the Ultimate-Hosts-Blacklist project.

Provide some configurable variables.

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

from os import getcwd
from os import sep as directory_separator


class Outputs:
    """
    Provide some configurations.
    """

    # The current directory path.
    current_directory = getcwd() + directory_separator

    # The name of the file where we save the input
    # source list.
    input_destination = "{0}domains.list".format(current_directory)

    # The name of the file where we save the input
    # source list cleaned with the help of PyFunceble.
    clean_destination = "{0}clean.list".format(current_directory)

    # The name of the file where we save the input
    # source list cleaned with our whitelisting tool.
    whitelisted_destination = "{0}whitelisted.list".format(current_directory)

    # The name of the file where we save the input
    # source list cleaned with the help of PyFunceble without the SPECIAL rules.
    volatile_destination = "{0}volatile.list".format(current_directory)


class PyFunceble:
    """
    Provide some configuration for the usage of PyFunceble.
    """

    # Some list of links we may use.
    links = {
        "production_config": {
            "link": "https://raw.githubusercontent.com/funilrys/PyFunceble/master/.PyFunceble_production.yaml",
            "destination": ".PyFunceble_production.yaml",
        },
        "license": {
            "link": "https://raw.githubusercontent.com/funilrys/PyFunceble/master/LICENSE",
            "destination": ".PyFunceble_LICENSE",
        },
    }

    # Tell us if we have to install the dev version.
    stable = True

    # The configuration indexes to update
    configuration = {
        "less": False,
        "plain_list_domain": True,
        "seconds_before_http_timeout": 6,
        "share_logs": True,
        "show_execution_time": True,
        "split": True,
        "travis": True,
        "travis_autosave_commit": "[Autosave] Testing for Ultimate Hosts Blacklist",
        "travis_autosave_final_commit": "[Results] Testing for Ultimate Hosts Blacklist",
        "travis_autosave_minutes": 15,
        "idna_conversion": True,
    }


class Infrastructure:
    """
    Provide some configuration around our infrastructure.
    """

    links = {
        "license": {
            "link": "https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/repository-structure/master/LICENSE",
            "destination": "LICENSE",
        },
        "config": {
            "link": "https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/repository-structure/master/.PyFunceble_cross_input_sources.yaml",
            "cross_destination": ".PyFunceble_cross_input_sources.yaml",
            "destination": ".PyFunceble.yaml",
        },
    }

    markers = {"launch_test": r"Launch\stest"}

    administration_file = "{0}info.json".format(Outputs.current_directory)

    should_be_bool = ["currently_under_test"]

    should_be_int = ["days_until_next_test", "last_test"]

    unneeded_indexes = ["arguments", "clean_original", "stable"]
