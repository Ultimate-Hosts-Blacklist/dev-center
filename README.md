# Ultimate Hosts Blacklist whitelisting script

This branch will help you clean your list or host file with the whitelist list which is used by the [Ultimate Hosts Blacklist](https://github.com/mitchellkrogza/Ultimate.Hosts.Blacklist) infrastructure.

## Requirements

If you want to use the script, please take the time to clone this branch and install the requirements with:

    pip3 install --user -r requirements.txt

## Complementary whitelist

Our script allow us to link one or more file(s) to the system which will be used in complementary of our whitelist list.

### Special markers

If you already used a whitelist list you already know that we generaly only list all domains we want to whitelist one by one.

It's also possible to do that with our whitelisting system but we can do more.

#### `ALL ` 

The `ALL ` marker will tell the system to escape and regex check againt what follows.

##### INVALID characters

* `$`
    * As we automatically append `$` to the end, you should not use this character.

* `\`
    * As we automatically escape the given expression, you should not explicitly escape your regular expression when declaring an `ALL ` marker.


#### `REG ` 

The `REG ` marker will tell the system to explicitly check for the given regex which follows the marker.

#### `RZD `

The `RZD ` marker will tell the system to explicitly check for the given string plus all possible TDL.

### Understanding what we actually do

If we have the following secondary whitelist list:

```
facebook.com
ALL .gov
REG face
RZD ebay
```

our system will actually :

* Remove every line which match `facebook.com` and `www.facebook.com`
* Remove everyline which match `ebay.*`
* In complementary convert all lines with `ALL ` or `REG` to the right format.
* Check every line again the regular expression.
* Print or save on screen the results.

The genereated regular expression will be in this example:

```re
\.gov$|face|ebay(.*)
```

**NOTE: The ebay group is much longer as we construct the list of TDL based on the Root Zone Database of the IANA and the Public Suffix List project.**

Which actually means that we whitelist:

* all elements/lines which ends with `.gov`
* all elements/lines which contain the word `face`

## Usage of the script

    usage: whitelisting.py [-h] [-f FILE] [-w WHITELIST [WHITELIST ...]] [-wc]
                        [-o OUTPUT]

    The tool to whitelist a list or a hosts file with the Ultimate Hosts Blacklist
    infrastructure.

    optional arguments:
    -h, --help            show this help message and exit
    -f FILE, --file FILE  Read the given file and remove all element to
                            whitelist.
    -w WHITELIST [WHITELIST ...], --whitelist WHITELIST [WHITELIST ...]
                            Read the given file and append its data to the our
                            whitelist list.
    -wc, --without-core   Disable the usage of the Ultimate Hosts Blacklist
                            whitelist list.
    -o OUTPUT, --output OUTPUT
                            Save the result to the given filename or path.

    Crafted with ♥ by Nissar Chababy (Funilrys)

