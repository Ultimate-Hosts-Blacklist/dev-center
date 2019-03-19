"""
The tool to update the central repository of the Ultimate-Hosts-Blacklist project.

Provide the input source (repositories) informations.

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
from os import path

from requests import get

from ultimate_hosts_blacklist.central_repo_updater.configuration import (
    GitHub,
    Infrastructure,
    Output,
)
from ultimate_hosts_blacklist.helpers import Dict, File, Regex


class Repositories:  # pylint: disable=too-few-public-methods
    """
    Provide the list of repositories we are going to work with.
    """

    regex_next_url = r"(?:.*\<(.*?)\>\;\s?rel\=\"next\")"

    def __init__(self):
        self.first_url_to_get = "{0}/repos?sort=created&direction=desc".format(
            GitHub.complete_api_orgs_url
        )
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": "token %s",
        }

        if path.isfile(Output.etags_file):
            self.etags = Dict.from_json(File(Output.etags_file).read())
        else:
            self.etags = {}

        if GitHub.api_token:
            self.headers["Authorization"] %= GitHub.api_token
        else:
            del self.headers["Authorization"]

    def get(self, url_to_get=None):  # pylint: disable=too-many-branches
        """
        Return the data from the API or the local file
        if nothing changes.

        :param url_to_get: The url to get next.
        :type url_to_get: str
        """

        next_url = None

        if not url_to_get:
            url_to_get = self.first_url_to_get

        if self.etags and url_to_get in self.etags:
            self.headers["If-None-Match"] = self.etags[url_to_get]

        req = get(url_to_get, headers=self.headers)

        if req.status_code == 200:
            data = req.json()
            repos = []

            if "Etag" in req.headers:
                self.etags[url_to_get] = req.headers["Etag"]
                Dict(self.etags).to_json(Output.etags_file)

            if isinstance(data, list):
                repos.extend(data)
            else:
                raise NotImplementedError(
                    "Unable to understand GitHub API reponse for {0}".format(
                        repr(url_to_get)
                    )
                )

            if "Link" in req.headers:
                next_url = Regex(
                    req.headers["Link"], self.regex_next_url, group=1, return_data=True
                ).match()

                if next_url:
                    for element in self.get(url_to_get=next_url):
                        if element["name"] not in Infrastructure.repositories_to_ignore:
                            yield element
                        else:
                            continue

            if repos:
                for element in repos:
                    if element["name"] not in Infrastructure.repositories_to_ignore:
                        yield element
                    else:
                        continue
        elif req.status_code == 304:
            data = Dict.from_json(File(Output.repos_file).read())

            for element in data:
                if element["name"] not in Infrastructure.repositories_to_ignore:
                    yield element
                else:
                    continue
        elif req.status_code == 401:
            raise Exception("Bad GitHub credentials.")
        else:
            raise NotImplementedError(
                "Something went wrong while communicating with {0}".format(
                    repr(url_to_get)
                )
            )
