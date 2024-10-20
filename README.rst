=========
getoptify
=========

Overview
--------

``getoptify`` allows getopt parsing followed by deparsing, e.g. for allowing abbreviations with ``click`` or to enforce parser simplicity.

Installation
------------

To install ``getoptify``, you can use ``pip``. Open your terminal and run:

.. code-block:: bash

    pip install getoptify

Functions
---------

.. code-block:: python

    def command(*_args, **_kwargs):
        return functools.partial(decorator, *_args, **_kwargs)

    def decorator(old, /, *_args, **_kwargs):
        @functools.wraps(old)
        def new(args=None):
            args = process(args, *_args, **_kwargs)
            return old(args)

        return new

    def process(args=None, shortopts="", longopts=[], allow_argv=True, gnu=True):
        ...
        # this function is the heart of getoptify
        # args are parsed using getopt and then converted back into a list of args
        # allow_argv allows to default to sys.argv[1:] if args is None
        # if gnu then getopt.gnu_getopt is used else getopt.getopt

Recommended Usage
-----------------

.. code-block:: python

    @getoptify.command(shortopts="h", longopts=["foo", "bar="])
    def example(args=None):
        ...
        # here internal parsing

License
-------

This project is licensed under the MIT License.

Links
-----

* `Documentation <https://pypi.org/project/getoptify>`_
* `Download <https://pypi.org/project/getoptify/#files>`_
* `Source <https://github.com/johannes-programming/getoptify>`_

Credits
-------

* Author: Johannes
* Email: johannes-programming@mailfence.com

Thank you for using ``getoptify``!