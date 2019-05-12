"""
The helpers classes/function of the Ultimate-Hosts-Blacklist project.

Provide the helpers we use when user multiple process.

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
from multiprocessing import Pipe, Process
from traceback import format_exc


class OurProcessWrapper(Process):  # pragma: no cover
    """
    Wrapper of Process.
    The object of this class is just to overwrite :code:`Process.run()`
    in order to catch exceptions.
    .. note::
        This class takes the same arguments as :code:`Process`.
    """

    def __init__(self, *args, **kwargs):
        super(OurProcessWrapper, self).__init__(*args, **kwargs)

        self.conn1, self.conn2 = Pipe()
        self._exception_receiver = None

    def run(self):
        """
        Overwrites :code:`Process.run()`.
        """

        try:
            # We run a normal process.
            Process.run(self)

            # We send None as message as there was no exception.
            self.conn2.send(None)
        except Exception as exception:  # pylint: disable= broad-except
            # We get the traceback.
            traceback = format_exc()
            # We send the exception and its traceback to the pipe.
            self.conn2.send((exception, traceback))

    @property
    def exception(self):
        """
        Provide a way to check if an exception was send.
        """

        if self.conn1.poll():
            # There is something to read.

            # We get and save the exception.
            self._exception_receiver = self.conn1.recv()

        return self._exception_receiver
