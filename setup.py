"""
The tool to update the input repositories of the Ultimate-Hosts-Blacklist project.

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

from re import compile as comp
from re import sub as substring

from setuptools import setup

NAMESPACE = "ultimate_hosts_blacklist"
MODULE = "input_repo_updater"

PYPI_NAME = substring(r"_", r"-", "{0}-{1}".format(NAMESPACE, MODULE))


def _get_requirements():
    """
    Extract all requirements from requirements.txt.
    """

    with open("requirements.txt") as file:
        requirements = file.read().splitlines()

    return requirements


def _get_version():
    """
    Extract the version from ultimate_hosts_blacklist/MODULE/__init__.py
    """

    to_match = comp(r'VERSION\s=\s"(.*)"\n')
    extracted = to_match.findall(
        open(
            "ultimate_hosts_blacklist/{0}/__init__.py".format(MODULE), encoding="utf-8"
        ).read()
    )[0]

    return ".".join(list(filter(lambda x: x.isdigit(), extracted.split("."))))


def _get_long_description():  # pragma: no cover
    """
    This function return the long description.
    """

    return open("README.rst", encoding="utf-8").read()


if __name__ == "__main__":
    setup(
        name=PYPI_NAME,
        version=_get_version(),
        install_requires=_get_requirements(),
        description="The tool to update the input source repositories of the Ultimate-Hosts-Blacklist project.",  # pylint: disable=line-too-long
        long_description=_get_long_description(),
        license="MIT",
        url="https://github.com/Ultimate-Hosts-Blacklist/dev-center/tree/input-repo-updater",
        platforms=["any"],
        packages=["ultimate_hosts_blacklist.{0}".format(MODULE)],
        keywords=["Python", "hosts", "hosts file"],
        classifiers=[
            "Environment :: Console",
            "Topic :: Internet",
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
        ],
        entry_points={
            "console_scripts": [
                "uhb_input_repo_updater=ultimate_hosts_blacklist.{0}:_command_line".format(
                    MODULE
                ),
                "uhb-input-repo-updater=ultimate_hosts_blacklist.{0}:_command_line".format(
                    MODULE
                ),
                "ultimate-hosts-blacklist-input-repo-updater=ultimate_hosts_blacklist.{0}:_command_line".format(  # pylint: disable=line-too-long
                    MODULE
                ),
            ]
        },
    )
