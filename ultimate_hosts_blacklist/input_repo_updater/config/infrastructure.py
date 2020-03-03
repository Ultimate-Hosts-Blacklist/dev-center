"""
The tool to update the input repositories of the Ultimate-Hosts-Blacklist project.

Provides our Infrastructure related configuration.

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


class Infrastructure:  # pylint: disable=too-few-public-methods
    """
    Provides some configuration around our infrastructure.
    """

    # Set our infrastructure links.
    links_stable = {
        "license": {
            "link": "https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/repository-structure/master/LICENSE",  # pylint: disable=line-too-long
            "destination": "LICENSE",
        },
        "config": {
            "link": "https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/repository-structure/master/.PyFunceble_cross_input_sources.yaml",  # pylint: disable=line-too-long
            "cross_destination": ".PyFunceble_cross_input_sources.yaml",
            "destination": ".PyFunceble.yaml",
        },
        "travis_config": {
            "link": "https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/repository-structure/master/.travis.yml"  # pylint: disable=line-too-long
        },
        "requirements": {
            "link": "https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/repository-structure/master/requirements.txt",  # pylint: disable=line-too-long
            "destination": "requirements.txt",
        },
    }

    links_dev = {
        "license": {
            "link": "https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/repository-structure/dev/LICENSE",  # pylint: disable=line-too-long
            "destination": "LICENSE",
        },
        "config": {
            "link": "https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/repository-structure/dev/.PyFunceble_cross_input_sources.yaml",  # pylint: disable=line-too-long
            "cross_destination": ".PyFunceble_cross_input_sources.yaml",
            "destination": ".PyFunceble.yaml",
        },
        "travis_config": {
            "link": "https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/repository-structure/dev/.travis.yml"  # pylint: disable=line-too-long
        },
        "requirements": {
            "link": "https://raw.githubusercontent.com/Ultimate-Hosts-Blacklist/repository-structure/dev/requirements.txt",  # pylint: disable=line-too-long
            "destination": "requirements.txt",
        },
    }

    # Set the default version to use if not declared.
    default_version = "stable"

    # Set our makers list.
    markers = {"launch_test": r"Launch\stest"}

    # List indexes in the administration file and how we interpret them.
    should_be_bool = ["currently_under_test"]
    should_be_int = ["days_until_next_test", "last_test"]
    should_be_dict = ["custom_pyfunceble_config"]
    should_be_datetime = ["end_datetime", "start_datetime", "last_autosave_datetime"]
    should_be_epoch_datetime = ["start_epoch", "end_epoch", "last_autosave_epoch"]
    unneeded_indexes = ["arguments", "clean_original", "stable", "last_test"]

    # Set the commit message to send when updating the travis configuration.
    travis_config_update_message = "Update of the Travis CI configuration file"

    # Set the commit message to send when updateing the PyFunceble configuration file.
    pyfunceble_config_update_message = "Update of the configuration file of PyFunceble"

    @classmethod
    def is_version_known(cls, name):
        """
        Checks if the given version is known.
        """

        try:
            _ = getattr(cls, f"links_{name.lower()}")
            return True
        except AttributeError:
            pass

        return False
