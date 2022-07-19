compose-operator
================

This module allows adding function composition with the ``|``
operator to any function, method, class, or other callable.

Great care is taken to ensure that

1. adding the ``|`` operator does not interfere with any other
   functionality, such as other operators, type checks, type and that
``|``-composed results behave as much as possible like a
normal function, including signature introspection, method
binding behavior, pickling, and so on. In particular,
|wrapt|_ is used to provide a wrapper that unintrusively and
transparently adds the ``|`` operator overload, and |compose|_
is used for the actual function composition implementation.

.. |wrapt| replace:: ``wrapt``
.. _wrapt: https://pypi.org/project/wrapt
.. |compose| replace:: ``compose``
.. _compose: https://pypi.org/project/compose


Versioning
----------

This library's version numbers follow the `SemVer 2.0.0
specification <https://semver.org/spec/v2.0.0.html>`_.


Installation
------------

::

    pip install compose-operator


Usage
-----

Basics
~~~~~~

Import ``composable``:

.. code:: python

    >>> from compose_operator import composable

A simple inline composition:

.. code:: python

    >>> stringify_as_integer = composable(int) | str
    >>> stringify_as_integer(12.3)
    '12'

Either side of the operation can be marked composable:

.. code:: python

    >>> stringify_as_integer = int | composable(str)
    >>> stringify_as_integer(12.3)
    '12'



Composable Classes
~~~~~~~~~~~~~~~~~~

Classes can be composable in two ways:

1. the class *instances* can be callable, typically by having the class
   define the ``__call__`` method.

