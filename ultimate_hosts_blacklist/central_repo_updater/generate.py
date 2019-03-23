"""
The tool to update the central repository of the Ultimate-Hosts-Blacklist project.

Provide the interface for file generation.

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
# pylint: disable=bad-continuation
from os import makedirs, path, walk

from ultimate_hosts_blacklist.central_repo_updater import logging
from ultimate_hosts_blacklist.central_repo_updater.configuration import (
    Infrastructure,
    Output,
    Templates,
    directory_separator,
)
from ultimate_hosts_blacklist.helpers import File, Regex


class Generate:
    """
    Provide the interface for file generation.
    """

    @classmethod
    def _next_file(
        cls,
        directory_path,
        filename,
        format_to_apply,
        subject,
        template=None,
        endline=None,
    ):  # pylint: disable= too-many-arguments, too-many-locals
        """
        Generate the next file.

        :param directory_path: The directory we are writting to.
        :type directory_path: str

        :param filename: The name of the file we are writting to.
        :type filename: str

        :param format_to_apply: The format to apply to a line.
        :type format_to_apply: str

        :param subject: The list of element to write/format.
        :type subject: list

        :param template: The template to write before generating each lines.
        :type template: str

        :param endline: The last line to write.
        :type endline: str
        """

        if path.isdir(directory_path):
            for root, _, files in walk(directory_path):
                for file in files:
                    File("{0}{1}{2}".format(root, directory_separator, file)).delete()
        else:
            makedirs(directory_path)

        i = 0
        last_element_index = 0

        while True:
            broken = False
            destination = "{0}{1}".format(directory_path, filename.format(i))

            logging.info("Generation of {0}".format(destination))
            with open(destination, "w", encoding="utf-8") as file:
                if not i and template:
                    logging.debug("Writting template:\n {0}".format(template))
                    file.write(template)

                for element in subject[last_element_index:]:
                    file.write("{0}\n".format(format_to_apply.format(element)))
                    last_element_index += 1

                    if file.tell() >= Output.max_file_size_in_bytes:
                        logging.info("Reached the desired size. Closing file.")

                        i += 1
                        broken = True

                        break
                if broken:
                    continue

                if endline:
                    logging.debug("Writting last line: \n {0}".format(endline))
                    file.write(endline)
            break

    @classmethod
    def dotted(cls, subject):
        """
        Generate the dotted formatted file.

        :param subject: The subject we are working with.
        :type subject: list
        """

        cls._next_file(
            Output.dotted_directory, Output.incomplete_dotted_filename, ".{0}", subject
        )

    @classmethod
    def plain_text_domain(cls, subject):
        """
        Generate the plain text domain formatted file.

        :param subject: The subject we are working with.
        :type subject: list
        """

        cls._next_file(
            Output.plain_text_domains_directory,
            Output.incomplete_plain_text_domains_filename,
            "{0}",
            subject,
        )

    @classmethod
    def plain_text_ip(cls, subject):
        """
        Generate the plain text ip formatted file.

        :param subject: The subject we are working with.
        :type subject: list
        """

        cls._next_file(
            Output.plain_text_ips_directory,
            Output.incomplete_plain_text_ips_filename,
            "{0}",
            subject,
        )

    @classmethod
    def hosts_deny(cls, subject):
        """
        Generate the hosts deny file.

        :param subject: The subject we are working with.
        :type subject: list
        """

        possible_template_file_location = "{0}hostsdeny.template".format(
            Output.current_directory
        )

        if Output.templates_dir and path.isfile(possible_template_file_location):
            template_base = File(possible_template_file_location).read()
        else:
            template_base = Templates.hosts_deny

        template = Regex(template_base, r"%%version%%").replace_with(
            Infrastructure.version
        )
        template = Regex(template, r"%%lenIP%%").replace_with(
            format(len(subject), ",d")
        )

        cls._next_file(
            Output.hosts_deny_directory,
            Output.incomplete_hosts_deny_filename,
            "ALL: {0}",
            subject,
            template=template,
            endline="# ##### END hosts.deny Block List # DO NOT EDIT #####",
        )

    @classmethod
    def superhosts_deny(cls, subject):
        """
        Generate the super hosts deny file.

        :param subject: The subject we are working with.
        :type subject: list
        """

        possible_template_file_location = "{0}superhostsdeny.template".format(
            Output.current_directory
        )

        if Output.templates_dir and path.isfile(possible_template_file_location):
            template_base = File(possible_template_file_location).read()
        else:
            template_base = Templates.superhosts_deny

        template = Regex(template_base, r"%%version%%").replace_with(
            Infrastructure.version
        )
        template = Regex(template, r"%%lenIPHosts%%").replace_with(
            format(len(subject), ",d")
        )

        cls._next_file(
            Output.superhosts_deny_directory,
            Output.incomplete_superhosts_deny_filename,
            "ALL: {0}",
            subject,
            template=template,
            endline="# ##### END Super hosts.deny Block List # DO NOT EDIT #####",
        )

    @classmethod
    def unix_hosts(cls, subject):
        """
        Generate the unix hosts file.

        :param subject: The subject we are working with.
        :type subject: list
        """

        possible_template_file_location = "{0}hosts.template".format(
            Output.current_directory
        )

        if Output.templates_dir and path.isfile(possible_template_file_location):
            template_base = File(possible_template_file_location).read()
        else:
            template_base = Templates.unix_hosts

        template = Regex(template_base, r"%%version%%").replace_with(
            Infrastructure.version
        )
        template = Regex(template, r"%%lenHosts%%").replace_with(
            format(len(subject), ",d")
        )

        cls._next_file(
            Output.unix_hosts_directory,
            Output.incomplete_unix_hosts_filename,
            "0.0.0.0 {0}",
            subject,
            template=template,
            endline="# END HOSTS LIST ### DO NOT EDIT THIS LINE AT ALL ###",
        )

    @classmethod
    def windows_hosts(cls, subject):
        """
        Generate the windows hosts file.

        :param subject: The subject we are working with.
        :type subject: list
        """

        possible_template_file_location = "{0}hosts.windows.template".format(
            Output.current_directory
        )

        if Output.templates_dir and path.isfile(possible_template_file_location):
            template_base = File(possible_template_file_location).read()
        else:
            template_base = Templates.windows_hosts

        template = Regex(template_base, r"%%version%%").replace_with(
            Infrastructure.version
        )
        template = Regex(template, r"%%lenHosts%%").replace_with(
            format(len(subject), ",d")
        )

        cls._next_file(
            Output.windows_hosts_directory,
            Output.incomplete_windows_hosts_filename,
            "127.0.0.1 {0}",
            subject,
            template=template,
            endline="# END HOSTS LIST ### DO NOT EDIT THIS LINE AT ALL ###",
        )

    @classmethod
    def readme_md(cls, len_domains, len_ips):
        """
        Generate the README.md file.

        :param domains: The number of domains.
        :type domains: int

        :param ips: The number of ips.
        :type ips: int
        """

        logging.info("Generation of {0}".format(repr(Output.readme_file)))

        possible_template_file_location = "{0}README_template.md".format(
            Output.current_directory
        )

        if Output.templates_dir and path.isfile(possible_template_file_location):
            template_base = File(possible_template_file_location).read()
        else:
            template_base = Templates.readme_md

        template = Regex(template_base, r"%%version%%").replace_with(
            Infrastructure.version
        )
        template = Regex(template, r"%%lenHosts%%").replace_with(
            format(len_domains, ",d")
        )
        template = Regex(template, r"%%lenIPs%%").replace_with(format(len_ips, ",d"))
        template = Regex(template, r"%%lenHostsIPs%%").replace_with(
            format(len_ips + len_domains, ",d")
        )

        File(Output.readme_file).write(template, overwrite=True)
