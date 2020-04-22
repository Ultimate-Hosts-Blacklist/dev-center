"""
The tool to update the input repositories of the Ultimate-Hosts-Blacklist project.

Provides the `domains.list` installer.

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
from tempfile import NamedTemporaryFile
from typing import Tuple, Union

import PyFunceble
from PyFunceble.helpers import Download, EnvironmentVariable, File

from ultimate_hosts_blacklist.whitelist import clean_list_with_official_whitelist

from ..config import Outputs
from ..exceptions import CouldNotDownload
from .base import InstallerBase


class DomainsListInstaller(InstallerBase):
    """
    Provides everything related to our infrastructure.
    """

    raw_link: int = None
    processes: int = 1

    def __init__(self, raw_link: Union[str, None], processes: int = 1) -> None:

        self.raw_link = raw_link
        self.processes = processes

        self.domains_list_destination = Outputs.input_destination

        self.files_to_clean = [
            Outputs.clean_destination,
            Outputs.whitelisted_destination,
            Outputs.volatile_destination,
        ]

        super().__init__()

    def authorization(self):
        return True

    @classmethod
    def get_subject(cls, line: str) -> Union[list, None]:
        """
        Provides (from a given line) the list of subjects
        we have to test.
        """

        return PyFunceble.converter.File(line).get_converted()

    def download_upstream(self) -> Union[str, None]:
        """
        Download the upstream file into a
        temporary file and return the newly created file.
        """

        if self.raw_link:
            file = NamedTemporaryFile(mode="r", delete=False)

            logging.info(
                "Started to download %s in %s", repr(self.raw_link), repr(file.name)
            )

            if not Download(self.raw_link).text(destination=file.name):
                raise CouldNotDownload(self.raw_link)

            logging.info(
                "Finished to download %s in %s", repr(self.raw_link), repr(file.name)
            )

            return file.name
        return None

    def get_diff_data(self, current_content, subjects) -> Tuple[set, set, set]:
        """
        Provides the difference data.
        """

        new = set()
        kept = set()

        if isinstance(subjects, list):
            for subject in subjects:
                new_new, kept_kept = self.get_diff_data(current_content, subject)

                new.update(new_new)
                kept.update(kept_kept)
        elif subjects in current_content:
            kept.add(subjects)
        else:
            new.add(subjects)

        return kept, new

    def get_diff(self, downloaded: Union[str, None]) -> Tuple[set, set, set]:
        """
        Given a path to the downloaded version, provides
        the new, removed and kept entries.
        """

        new = set()
        kept = set()
        removed = set()

        file_instance = File(self.domains_list_destination)

        if file_instance.exists():
            current_content = set(file_instance.read().splitlines())
        else:
            current_content = set()

        if downloaded:
            with open(downloaded, "r") as file_stream:
                for line in file_stream:
                    line = line.strip()

                    if not line:
                        continue

                    kept_kept, new_new = self.get_diff_data(
                        current_content, self.get_subject(line)
                    )

                    new.update(new_new)
                    kept.update(kept_kept)

            compare_base = kept.copy()
            compare_base.update(new)

            removed = current_content - compare_base
        else:
            kept = current_content

        return kept, removed, new

    def remove_from_all_files(self, to_remove):
        """
        Removes the given list from all files.
        """

        if to_remove:
            for file in self.files_to_clean:
                file_instance = File(file)

                if file_instance.exists():
                    logging.info(
                        "Started to sync the deletion from upstream into %s",
                        repr(file_instance.path),
                    )
                    new_version = clean_list_with_official_whitelist(
                        file_instance.read().splitlines(),
                        use_official=False,
                        your_whitelist_list=list(to_remove),
                        multiprocessing=True,
                        processes=self.processes
                        if not EnvironmentVariable("TRAVIS_BUILD_DIR").exists()
                        else 60,
                    )

                    file_instance.write("\n".join(new_version) + "\n", overwrite=True)
                    logging.info(
                        "Finished to sync the deletion from upstream into %s",
                        repr(file_instance.path),
                    )

    def start(self):
        logging.info(
            "Authorized to install %s: %s",
            self.domains_list_destination,
            self.authorized,
        )

        downloaded = self.download_upstream()

        kept, removed, new = self.get_diff(downloaded)

        to_write = kept.copy()
        to_write.update(new)

        logging.info(
            "Started to write the new version of %s",
            repr(self.domains_list_destination),
        )
        File(self.domains_list_destination).write(
            "\n".join(to_write) + "\n", overwrite=True
        )
        logging.info(
            "Finished to write the new version of %s",
            repr(self.domains_list_destination),
        )

        if downloaded is not None:
            File(downloaded).delete()

        self.remove_from_all_files(removed)
