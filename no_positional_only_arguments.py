# SPDX-License-Identifier: 0BSD
# Copyright 2022 Alexander Kozhevnikov <mentalisttraceur@gmail.com>

"""Operator overload for function composition."""

__all__ = ('composable', 'composable_constructor', 'composable_instances')
__version__ = '0.2.3'


from compose import sacompose as _compose
from wrapt import ObjectProxy as _ObjectProxy
import reprshed as _reprshed


def _name(obj):
    return type(obj).__name__


class composable(_ObjectProxy):
    """Make a function composable with the | operator."""
    __slots__ = ()

    def __init__(self, function):
        """Initialize the composable wrapper.

        Arguments:
            function: Function (or other callable) to make composable.

        Raises:
            TypeError: If the function is not callable.
        """
        if isinstance(function, (composable, composable_constructor)):
            function = function.__wrapped__
        if not callable(function):
            raise TypeError(_name(self) + '() argument must be callable')
        super(composable, self).__init__(function)

    def __or__(self, other):
        """Function composition operator overload.

        The composed function is equivalent to other(self(...)).
        """
        if not callable(other):
            return NotImplemented
        return type(self)(_compose(other, self))

    def __ror__(self, other):
        """Function composition operator overload.

        The composed function is equivalent to self(other(...)).
        """
        if not callable(other):
            return NotImplemented
        return type(self)(_compose(self, other))

    def __call__(*args, **kwargs):
        """Call the wrapped callable."""
        def __call__(self, *args):
            return self, args
        self, args = __call__(*args)
        return self.__wrapped__(*args, **kwargs)

    def __repr__(self):
        """Represent the composable wrapper as an unambiguous string."""
        return _reprshed.pure(self, self.__wrapped__)

    def __reduce_ex__(self, protocol):
        """Reduce the composable wrapper for copying or serialization."""
        return (type(self), (self.__wrapped__,))


class composable_constructor(_ObjectProxy):
    """Make a class constructor composable with the | operator."""
    __slots__ = ()

    def __init__(self, cls):
        """Initialize the composable wrapper.

        Arguments:
            cls: Class whose constructor to make composable.

        Raises:
            TypeError: If cls is not a class.
        """
        if isinstance(cls, (composable, composable_constructor)):
            cls = cls.__wrapped__
        if not isinstance(cls, type):
            raise TypeError(_name(self) + '() argument must be a class')
        super(composable_constructor, self).__init__(cls)

    def __or__(self, other):
        """Type union or function composition operator overload.

        If the other operand a type (which is not being forced
        to be composable), this operator falls through to what
        the wrapped object and the other operand would do. For
        classes as of Python 3.10, that creates a type union.

        If the other operand is not a type, or is being forced
        to be composable, this operator creates a composed
        function which is equivalent to other(self(...)).
        """
        if isinstance(other, type) and not isinstance(other, composable):
            return self.__wrapped__ | other
        if not callable(other):
            return NotImplemented
        return composable(_compose(other, self))

    def __ror__(self, other):
        """Type union or function composition operator overload.

        If the other operand a type (which is not being forced
        to be composable), this operator falls through to what
        the wrapped object and the other operand would do. For
        classes as of Python 3.10, that creates a type union.

        If the other operand is not a type, or is being forced
        to be composable, this operator creates a composed
        function which is equivalent to self(other(...)).
        """
        if isinstance(other, type) and not isinstance(other, composable):
            return other | self.__wrapped__
        if not callable(other):
            return NotImplemented
        return composable(_compose(self, other))

    __call__ = composable.__call__
    __repr__ = composable.__repr__
    __reduce_ex__ = composable.__reduce_ex__


class composable_instances(_ObjectProxy):
    """Make callable class instances composable with the | operator."""
    __slots__ = ()

    def __init__(self, cls):
        """Initialize the composable wrapper.

        Arguments:
            cls: Class whose callable instances to make composable.

        Raises:
            TypeError: If cls is not a class.
        """
        if not isinstance(cls, type):
            raise TypeError(_name(self) + '() argument must be a class')
        super(composable_instances, self).__init__(cls)

    def __call__(*args, **kwargs):
        """Construct a composable instance of the wrapped class."""
        def __call__(self, *args):
            return self, args
        self, args = __call__(*args)
        return composable(self.__wrapped__(*args, **kwargs))

    __repr__ = composable.__repr__
    __reduce_ex__ = composable.__reduce_ex__
