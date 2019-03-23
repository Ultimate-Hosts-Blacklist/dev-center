"""
The helpers classes/function of the Ultimate-Hosts-Blacklist project.

Provide the helpers we use for Shell command execution.

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

from subprocess import PIPE, Popen


class Command:
    """
    Shell command execution.

    :param command: The command to execute.
    :type command: str

    :param allow_stdout: Tell us if we are allowed to print stdout or not.
    :param allow_stdout: bool
    """

    def __init__(self, command, allow_stdout=True, encoding="utf-8"):
        self.decode_type = encoding
        self.command = command

        if not allow_stdout:
            self.process = Popen(self.command, stdout=PIPE, stderr=PIPE, shell=True)
        else:
            self.process = Popen(self.command, stderr=PIPE, shell=True)

    def decode_output(self, to_decode):
        """
        Decode the output of a shell command in order to be readable.

        :param to_decode: The line to decode.
        :type to_decode: bytes
        """
        if to_decode is not None:
            return str(to_decode, self.decode_type)
        return False

    def execute(self):
        """
        Execute the given command and wait until it ends to return its output.
        """

        (output, error) = self.process.communicate()

        if self.process.returncode != 0:
            decoded = self.decode_output(error)

            if not decoded:
                return "Unkown error. for %s" % (self.command)

            print(decoded)
            exit(1)
        return self.decode_output(output)

    def run_command(self):
        """
        Run the given command and return its output directly to stdout.
        """

        while True:
            current_line = self.process.stdout.readline().rstrip()

            if not current_line:
                break

            yield self.decode_output(current_line)
