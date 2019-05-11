"""
The helpers classes/function of the Ultimate-Hosts-Blacklist project.

Provide the helpers we use for document dowmload.

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

from shutil import copyfileobj

from requests import get

from ultimate_hosts_blacklist.helpers.file import File


class Download:  # pylint: disable=too-few-public-methods  # pragma: no cover
    """
    This class will initiate a download of the desired link.

    :param link_to_download:
        The link to the document we are going to download.
    :type link_to_download: str

    :param destination:
        The destinaion of the downloaded data.

        .. note::
            If :code:`None` is given, we return the document
            text.
    :type destination: str|None
    """

    def __init__(self, link_to_download, destination, convert_to_idna=False):
        self.link_to_download = link_to_download
        self.destination = destination
        self.convert_to_idna = convert_to_idna

    def _convert_to_idna(self, data):
        """
        This method convert a given data into IDNA format.

        :param data: The downloaded data.
        :type data: str

        .. warning::
            This method might be depracted anytime soon because
            a better implementation has to be written.
        """

        if self.convert_to_idna:
            to_write = []

            for line in data.split("\n"):
                line = line.split()
                try:
                    if isinstance(line, list):
                        converted = []
                        for string in line:
                            converted.append(string.encode("idna").decode("utf-8"))

                        to_write.append(" ".join(converted))
                    else:
                        to_write.append(line.encode("idna").decode("utf-8"))
                except UnicodeError:
                    if isinstance(line, list):
                        to_write.append(" ".join(line))
                    else:
                        to_write.append(line)
            return to_write
        return None

    def text(self):
        """
        Download the text response of the link.
        """

        if self.link_to_download:
            request = get(self.link_to_download)

            if request.status_code == 200:
                if self.destination:
                    File(self.destination).write(request.text, overwrite=True)
                    return True
                return request.text
        return False

    def stream(self):
        """
        Dowload the stream/file link.
        """

        if self.link_to_download:
            request = get(self.link_to_download, stream=True)

            if request.status_code == 200:
                request.raw.decode_content = True

                if self.destination:
                    with open(self.destination, "wb") as file:
                        copyfileobj(request.raw, file)
                    return True

                return request.raw
        return False

    def link(self):
        """
        This method initiate the download.
        """

        if self.link_to_download:
            request = get(self.link_to_download)

            if request.status_code == 200:
                if self.destination:
                    if self.convert_to_idna:
                        File(self.destination).write(
                            "\n".join(self._convert_to_idna(request.text)),
                            overwrite=True,
                        )
                    else:
                        File(self.destination).write(request.text, overwrite=True)
                    return True
                return request.text
        return False
