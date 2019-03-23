"""
The helpers classes/function of the Ultimate-Hosts-Blacklist project.

Provide the helpers we use for Travis container initialization..

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
from os import environ
from os import sep as directory_separator

from ultimate_hosts_blacklist.helpers.command import Command


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

            Command("git remote rm origin", True).execute()

            Command(
                "git remote add origin https://"
                + "%s@github.com/%s.git"
                % (environ["GH_TOKEN"], environ["TRAVIS_REPO_SLUG"]),
                True,
            ).execute()

            Command(
                'git config --global user.email "%s"' % (environ["GIT_EMAIL"]), True
            ).execute()

            Command(
                'git config --global user.name "%s"' % (environ["GIT_NAME"]), True
            ).execute()

            Command("git config --global push.default simple", True).execute()

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
                Command(command, True).execute()

            if Command("git config core.sharedRepository", False).execute() == "":
                Command("git config core.sharedRepository group", False).execute()
        except KeyError:
            pass
