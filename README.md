# Ultimate Hosts Blacklist comparison system

This branch will help us and/or you to know how many domains or IPs from a given list are not already present in the [Ultimate Hosts Blacklist](https://github.com/mitchellkrogza/Ultimate.Hosts.Blacklist) infrastructure.

Please also note that this repository and its comparison results are going to be (in the future) a factor of the introduction or non-introduction of a list into our infrastructure!

## Procedure for comparison

### Automated system as the preferred method

We set up this branch to automatically compare your list with our infrastructure with the help of Travis CI!

Simply fork this repository, checkout this branch, edit `info.json`, submit Pull Request and get the results from Travis CI tests!

Here is a short explanation of the `info.json`:

We use only 3 indexes: `name`, `link` and `file`.

#### `name`

To simplify our procedure when we are going to add your list to our infrastructure, we invite you to set a name.
Please note that the given name is probably going to be used as part of the repository name which will be set up for your list.

#### `link`

Want to compare with a Raw Link? Set your link this index and we will compare it automatically!

#### `file`

Want to compare a file? Simply add your file to your branch and add its name here and we will compare it automatically!

### Clone and run

If you want to run a test locally simply install the requirements with

    pip3 install -r requirements.txt

and use the script!

#### Usage of the script

    usage: compare_with_upstream.py [-h] [-l LINK] [-f FILE]

    A script to compare a given link or file to Ultimate.Hosts.Blacklist
    infrastructure.

    optional arguments:
      -h, --help            show this help message and exit
      -l LINK, --link LINK  Link to compare.
      -f FILE, --file FILE  File to compare.

    Crafted with ♥ by Nissar Chababy (Funilrys)
