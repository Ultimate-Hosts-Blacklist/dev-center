"""
The tool to update the central repository of the Ultimate-Hosts-Blacklist project.

Provide the Travis pre-configuration logic.

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

from ultimate_hosts_blacklist.central_repo_updater import logging
from ultimate_hosts_blacklist.central_repo_updater.configuration import (
    directory_separator,
    environ,
)
from ultimate_hosts_blacklist.helpers import Command


class TravisCI:
    """
    Preconfigure and manage the container.
    """

    @classmethod
    def configure_git_repo(cls):
        """
        Configure Git and the local repository for future push.
        """

        try:
            _ = environ["TRAVIS_BUILD_DIR"]

            logging.info("Deletion of remote origin")
            Command("git remote rm origin", True).execute()

            logging.info("Adding the right remote origin URL")
            Command(
                "git remote add origin https://"
                + "%s@github.com/%s.git"
                % (environ["GH_TOKEN"], environ["TRAVIS_REPO_SLUG"]),
                True,
            ).execute()

            logging.info("Updating git.user.email")
            Command(
                'git config --global user.email "%s"' % (environ["GIT_EMAIL"]), True
            ).execute()

            logging.info("Updating git.user.name")
            Command(
                'git config --global user.name "%s"' % (environ["GIT_NAME"]), True
            ).execute()

            logging.info("Update of git.push.default")
            Command("git config --global push.default simple", True).execute()

            logging.info("Checkout of {0}".format(repr(environ["GIT_BRANCH"])))
            Command("git checkout %s" % environ["GIT_BRANCH"], True).execute()
        except KeyError:
            pass

    @classmethod
    def fix_permissions(cls):
        """
        Fix the permissions of TRAVIS_BUILD_DIR.
        """

        try:
            build_dir = environ["TRAVIS_BUILD_DIR"]
            commands = [
                "sudo chown -R travis:travis %s" % (build_dir),
                "sudo chgrp -R travis %s" % (build_dir),
                "sudo chmod -R g+rwX %s" % (build_dir),
                "sudo chmod 777 -Rf %s.git" % (build_dir + directory_separator),
                r"sudo find %s -type d -exec chmod g+x '{}' \;" % (build_dir),
            ]

            for command in commands:
                logging.debug(command)
                Command(command, True).execute()

            if Command("git config core.sharedRepository", False).execute() == "":
                Command("git config core.sharedRepository group", False).execute()
        except KeyError:
            pass
