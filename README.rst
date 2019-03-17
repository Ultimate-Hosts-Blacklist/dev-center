The Ultimate Hosts Blacklist comparison tool
=============================================

This is the branch which contain the tool which let us compare a given list with our infrastructure.

Installation
------------

::

    $ pip3 install --user ultimate-hosts-blacklist-comparison


Usage
-----

The sript can be called as :code:`uhb-comparison`, :code:`uhb_comparison` and :code:`ultimate-hosts-blacklist-comparison`.

::

    usage: ultimate-hosts-blacklist-comparison [-h] [-c] [--clean] [-f FILE]
                                           [-l LINK] [--verbose]

    A script to compare a given link or file to Ultimate Hosts Blacklist
    infrastructure.

    optional arguments:
        -h, --help            show this help message and exit
        -c, --cache           Use cache if exist.
        --clean               Clean the given file/link with our official whitelist
                                tool before processing.
        -f FILE, --file FILE  File to compare.
        -l LINK, --link LINK  Link to compare.
        --verbose             Run in verbose mode.

    Crafted with ♥ by Nissar Chababy (Funilrys)
