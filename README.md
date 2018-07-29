# Ultimate Hosts Blacklist whitelisting script

This branch will help you clean your list or host file with the whitelist list which is used by the [Ultimate Hosts Blacklist](https://github.com/mitchellkrogza/Ultimate.Hosts.Blacklist) infrastructure.


## Procedure for whitelisting

### Clone and run

If you want to run a test locally simply install the requirements with

    pip3 install -r requirements.txt

and use the script!

#### Usage of the script

    usage: whitelisting.py [-h] [-f FILE] [-w WHITELIST] [-o OUTPUT]

    The tool to whitelist a list or a hosts file with the Ultimate Hosts Blacklist
    infrastructure.

    optional arguments:
    -h, --help            show this help message and exit
    -f FILE, --file FILE  Read the given file and remove all element to
                            whitelist.
    -w WHITELIST, --whitelist WHITELIST
                            Read the given file and append its data to the our
                            whitelist list.
    -o OUTPUT, --output OUTPUT
                            Save the result to the given filename or path.

    Crafted with ♥ by Nissar Chababy (Funilrys)

