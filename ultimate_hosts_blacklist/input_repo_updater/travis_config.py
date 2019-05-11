"""
The tool to update the input repositories of the Ultimate-Hosts-Blacklist project.

Provide the automatic sychronization of the travis configuration file.

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
# pylint: disable=wrong-import-order
import logging
from os import environ

from yaml import safe_dump as yaml_dump
from yaml import safe_load as yaml_load

from ultimate_hosts_blacklist.helpers import Command, Dict, Download, File
from ultimate_hosts_blacklist.input_repo_updater.configuration import Infrastructure


class TravisConfig:  # pylint: disable=bad-continuation, logging-format-interpolation
    """
    Provide an interface to automatically sychronize the travis configuration
    file accross all repositories.
    """

    # Saves the local version of the travis configuration file.
    local_version = {}
    # Saves the upstream (central) version of the travis configuration file.
    upstream_version = {}
    # Tell us which index we have to delete.
    to_delete = []
    # Tell us which index we have to update.
    to_update = [
        "install",
        "notifications",
        "addons",
        "cache",
        "dist",
        "language",
        "matrix",
        "python",
        "script",
        "sudo",
    ]

    def __init__(self):
        if not File(Infrastructure.admin_file).exists():
            self.get_current_local_version()
            self.get_central_version()
            self.save()
            self.check_changes_and_commit()

    @classmethod
    def check_changes_and_commit(cls):
        """
        Check if there was some changes into the configuration file.

        If it is the case, we commit the changes and exit the current instance.
        """

        if (
            Command(
                "git status --porcelain {0}".format(Infrastructure.travis_config_file),
                allow_stdout=False,
            )
            .execute()
            .strip()
            .startswith("M")
        ):
            try:
                _ = environ["GIT_BRANCH"]
                _ = environ["TRAVIS_BUILD_DIR"]

                logging.info(
                    "Stopping instance: New version of the Travis CI configuration file."
                )

                Command(
                    "git add {0} && git commit -m '{1}' && git push origin {2}".format(
                        Infrastructure.travis_config_file,
                        Infrastructure.travis_config_update_message,
                        environ["GIT_BRANCH"],
                    )
                ).execute()

                exit(0)
            except KeyError:
                pass

    def get_current_local_version(self):
        """
        Get the current local version.
        """

        try:
            _ = environ["GIT_BRANCH"]
            _ = environ["TRAVIS_BUILD_DIR"]

            logging.info(
                "Reading local version of {0}".format(
                    repr(Infrastructure.travis_config_file)
                )
            )
            content = File(Infrastructure.travis_config_file).read()
            logging.debug("Content: \n {0}".format(content))

            self.local_version = yaml_load(content)
        except KeyError:
            pass

    def get_central_version(self):
        """
        Get the upstream (central) version.
        """

        try:
            _ = environ["GIT_BRANCH"]
            _ = environ["TRAVIS_BUILD_DIR"]

            logging.info(
                "Getting central version of {0}".format(
                    repr(Infrastructure.travis_config_file)
                )
            )

            if Infrastructure.stable:
                link = Infrastructure.links["travis_config"]["link"].replace(
                    "dev", "master"
                )
            else:
                link = Infrastructure.links["travis_config"]["link"].replace(
                    "master", "dev"
                )

            upstream = Download(link, None).text()

            if isinstance(upstream, str):
                # The downloaded data is a str.

                logging.debug("Content: \n {0}".format(upstream))

                self.upstream_version = yaml_load(upstream)

                return None

            # Otherwise, we raise an exception, we can't do nothing without
            # something to test.
            raise Exception("Unable to get the content of {0}.".format(repr(link)))
        except KeyError:
            pass

    def merge(self):
        """
        Merge the two versions.
        """

        try:
            _ = environ["GIT_BRANCH"]
            _ = environ["TRAVIS_BUILD_DIR"]

            for index in self.to_update:
                logging.info(
                    "Merging {0} into {1} ".format(
                        index, repr(Infrastructure.travis_config_file)
                    )
                )

                self.local_version[index] = self.upstream_version[index]

            flattened = Dict(self.local_version).flatten(separator=".")

            for index in self.to_delete:
                logging.info(
                    "Deleting {0} from {1} ".format(
                        index, repr(Infrastructure.travis_config_file)
                    )
                )

                if index in flattened:
                    del flattened[index]

            self.local_version = Dict(flattened).unflatten(separato=".")
        except KeyError:
            pass

    def save(self):
        """
        Save the new local versions.
        """

        try:
            _ = environ["GIT_BRANCH"]
            _ = environ["TRAVIS_BUILD_DIR"]

            logging.debug(
                "Saving new version into {0}.".format(
                    repr(Infrastructure.travis_config_file)
                )
            )

            with open(
                Infrastructure.travis_config_file, "w", encoding="utf-8"
            ) as file_stream:
                new_version = yaml_dump(
                    self.local_version,
                    encoding="utf-8",
                    allow_unicode=True,
                    indent=4,
                    default_flow_style=False,
                ).decode("utf-8")

                logging.debug(
                    "New version of {0}: \n{1}".format(
                        repr(Infrastructure.travis_config_file), new_version
                    )
                )
                file_stream.write(new_version)
        except KeyError:
            pass
