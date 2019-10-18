"""
The tool to update the central repository of the Ultimate-Hosts-Blacklist project.

Provide the deployement logic.

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
from requests import get

from ultimate_hosts_blacklist.central_repo_updater.configuration import (
    Infrastructure,
    environ,
)
from ultimate_hosts_blacklist.helpers import Command, TravisCI


class Deploy:
    """
    Provide the deployement logic.
    """

    @classmethod
    def github(cls):
        """
        Deploy to GitHub.
        """

        try:
            _ = environ["TRAVIS_BUILD_DIR"]
            commit_message = "%s [ci skip]" % Infrastructure.version

            TravisCI().fix_permissions()

            Command(
                "git add --all && git commit -a -m '%s' && git push origin %s"
                % (commit_message, environ["GIT_BRANCH"]),
                False,
            ).execute()
        except KeyError:
            pass

    @classmethod
    def hosts_ubuntu101_co_za(cls):
        """
        Deploy to our mirror: hosts.ubuntu101.co.za.
        """

        get(Infrastructure.links["deploy"])
