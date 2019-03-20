The Ultimate Hosts Blacklist central repository updater
=======================================================

This is the branch which contain the tool which we use to update our `central repository`_ .

Installation
------------

::

    $ pip3 install --user ultimate-hosts-blacklist-central-repo-updater



Usage
-----

The sript can be called as :code:`uhb-central-repo-updater`, :code:`uhb_central_repo_updater` and :code:`ultimate-hosts-blacklist-central-repo-updater`.

::

    usage: uhb_central_repo_updater [-h] [-m] [-p PROCESSES]

    The tool to update the central repository of the Ultimate-Hosts-Blacklist
    project.

    optional arguments:
        -h, --help            show this help message and exit
        -m, --multiprocessing
                                Activate the usage of the multiprocessing.
        -p PROCESSES, --processes PROCESSES
                                The number of simulatenous processes to create and
                                use.

    Crafted with ♥ by Nissar Chababy (Funilrys)


.. _central repository: https://github.com/mitchellkrogza/Ultimate.Hosts.Blacklist


License
-------

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