"""
The tool to update the input repositories of the Ultimate-Hosts-Blacklist project.

Provides the configuration around the way we use PyFunceble.

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


class PyFunceble:
    """
    Provide some configuration for the usage of PyFunceble.
    """

    # Some list of links we may use.
    links_stable = {
        "production_config": {
            "link": "https://raw.githubusercontent.com/funilrys/PyFunceble/master/.PyFunceble_production.yaml",  # pylint: disable=line-too-long
            "destination": ".PyFunceble_production.yaml",
        },
        "license": {
            "link": "https://raw.githubusercontent.com/funilrys/PyFunceble/master/LICENSE",
            "destination": ".PyFunceble_LICENSE",
        },
    }

    links_dev = {
        "production_config": {
            "link": "https://raw.githubusercontent.com/funilrys/PyFunceble/dev/.PyFunceble_production.yaml",  # pylint: disable=line-too-long
            "destination": ".PyFunceble_production.yaml",
        },
        "license": {
            "link": "https://raw.githubusercontent.com/funilrys/PyFunceble/dev/LICENSE",
            "destination": ".PyFunceble_LICENSE",
        },
    }

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
        "ci": True,
        "auto_continue": True,
        "ci_autosave_commit": "[Autosave] Testing for Ultimate Hosts Blacklist",
        "ci_autosave_final_commit": "[Results] Testing for Ultimate Hosts Blacklist",
        "ci_autosave_minutes": 15,
        "idna_conversion": True,
        "dns_server": ["1.1.1.1", "1.0.0.1"],
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
    packages = {"stable": "PyFunceble", "dev": "PyFunceble-dev"}

    # Tell us the default package to use if not specified.
    default_package = "stable"

    @classmethod
    def is_package_known(cls, name):
        """
        Checks if the package that is given by the administration file is known.
        """

        return name in cls.packages

    @classmethod
    def get_package_to_install(cls, name):
        """
        Gets the package to install from the given name,
        """

        return (
            cls.default_package
            if not cls.is_package_known(name)
            else cls.packages[name]
        )
