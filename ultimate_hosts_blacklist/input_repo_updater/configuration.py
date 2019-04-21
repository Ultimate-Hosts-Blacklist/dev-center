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


class Outputs:  # pylint: disable=too-few-public-methods
    """
    Provide some configurations.
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
    # The name of the continue file.
    continue_filename = "continue.json"

    # The location of the input file.
    input_destination = "{0}{1}".format(current_directory, input_filename)

    # The location of the clean file.
    clean_destination = "{0}{1}".format(current_directory, clean_filename)

    # The location of the whitelisted file.
    whitelisted_destination = "{0}{1}".format(current_directory, whitelisted_filename)

    # The location of the volatile file.
    volatile_destination = "{0}{1}".format(current_directory, volatile_filename)

    # The location of the temporary volatile file.
    temp_volatile_destination = "{0}output{1}{2}".format(
        current_directory, directory_separator, volatile_filename
    )

    # The location of the continue file.
    continue_destination = "{0}output{1}{2}".format(
        current_directory, directory_separator, continue_filename
    )

    # The location of the list of ACTIVE domains.
    active_subjects_destination = "{0}output{1}domains{1}ACTIVE{1}list".format(
        current_directory, directory_separator
    )


class PyFunceble:  # pylint: disable=too-few-public-methods
    """
    Provide some configuration for the usage of PyFunceble.
    """

    # Some list of links we may use.
    links = {
        "production_config": {
            "link": "https://raw.githubusercontent.com/funilrys/PyFunceble/2.x.x/.PyFunceble_production.yaml",  # pylint: disable=line-too-long
            "destination": ".PyFunceble_production.yaml",
        },
        "license": {
            "link": "https://raw.githubusercontent.com/funilrys/PyFunceble/2.x.x/LICENSE",
            "destination": ".PyFunceble_LICENSE",
        },
    }

    # Tell us if we have to install the stable version.
    stable = False

    # The configuration indexes to update
    configuration = {
        "less": False,
        "no_files": False,
        "quiet": True,
        "plain_list_domain": True,
        "seconds_before_http_timeout": 6,
        "share_logs": True,
        "show_execution_time": False,
        "show_percentage": True,
        "split": False,
        "travis": True,
        "travis_autosave_commit": "[Autosave] Testing for Ultimate Hosts Blacklist",
        "travis_autosave_final_commit": "[Results] Testing for Ultimate Hosts Blacklist",
        "travis_autosave_minutes": 15,
        "idna_conversion": True,
    }

    # The configuration we are going to parse to the PyFunceble API.
    #
    # Note: You might think: WTF ! My response: We only use PyFunceble API and
    # not the CLI. So the following is required to keep running with the
    # same structure as previous.
    api_configuration = {
        "api_file_generation": True,
        "inactive_database": True,
        "no_files": False,
        "whois_database": True,
    }

    # Set the PyFunceble packages to install.
    packages = {
        "stable": "PyFunceble",
        "dev": "git+https://github.com/funilrys/PyFunceble.git@2.x.x",
    }


class Infrastructure:  # pylint: disable=too-few-public-methods
    """
    Provide some configuration around our infrastructure.
    """

    # Set our infrastructure links.
    links = {
        "license": {
            "link": "https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/repository-structure/master/LICENSE",  # pylint: disable=line-too-long
            "destination": "LICENSE",
        },
        "config": {
            "link": "https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/repository-structure/master/.PyFunceble_cross_input_sources.yaml",  # pylint: disable=line-too-long
            "cross_destination": ".PyFunceble_cross_input_sources.yaml",
            "destination": ".PyFunceble.yaml",
        },
    }

    # Set our makers list.
    markers = {"launch_test": r"Launch\stest"}

    # The path to the administration file.
    administration_file = "{0}info.json".format(Outputs.current_directory)

    # List indexes in the administration file and how we interpret them.
    should_be_bool = ["currently_under_test"]
    should_be_int = ["days_until_next_test", "last_test"]
    unneeded_indexes = ["arguments", "clean_original", "stable"]
