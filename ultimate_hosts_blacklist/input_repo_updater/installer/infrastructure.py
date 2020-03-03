"""
The tool to update the input repositories of the Ultimate-Hosts-Blacklist project.

Provides the infrastructure installer. It installs everything related to our
infrastructure.

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

import logging

from PyFunceble.helpers import Download

from ..config import Infrastructure
from ..exceptions import CouldNotDownload
from .base import InstallerBase


class InfrastructureInstaller(InstallerBase):
    """
    Provides everything related to our infrastructure.
    """

    def authorization(self):
        return True

    def start(self):
        logging.info("Authorized to install infrastructure files: %s", self.authorized)

        for data in getattr(
            Infrastructure, f"links_{self.infrastructure_version}"
        ).values():
            if "cross_destination" in data:
                continue

            if "destination" not in data or "link" not in data:
                continue

            if not Download(data["link"]).text(data["destination"]):
                raise CouldNotDownload(data["link"])
