# SPDX-License-Identifier: 0BSD
# Copyright 2022 Alexander Kozhevnikov <mentalisttraceur@gmail.com>

"""Operator overload for function composition."""

__all__ = ('composable', 'composable_constructor', 'composable_instances')
__version__ = '0.3.2'


from compose import sacompose as _compose
from wrapt import CallableObjectProxy as _CallableObjectProxy
import reprshed as _reprshed


try:
    _CallableObjectProxy(lambda self: None)(self=None)
except TypeError:
    class _CallableObjectProxy(_CallableObjectProxy):
        def __call__(*args, **kwargs):
            def __call__(self, *args):
                return self, args
            self, args = __call__(*args)
            return self.__wrapped__(*args, **kwargs)


def _name(obj):
    return type(obj).__name__


class composable(_CallableObjectProxy):
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

        The composed function is equivalent to other(self(...)),
        and is itself composable with the | operator.
        """
        if not callable(other):
            return NotImplemented
        return type(self)(_compose(other, self))

    def __ror__(self, other):
        """Function composition operator overload.

        The composed function is equivalent to self(other(...)),
        and is itself composable with the | operator.
        """
        if not callable(other):
            return NotImplemented
        return type(self)(_compose(self, other))

    def __repr__(self):
        """Represent the composable wrapper as an unambiguous string."""
        return _reprshed.pure(self, self.__wrapped__)

    def __reduce_ex__(self, protocol):
        """Reduce the composable wrapper for copying or serialization."""
        return (type(self), (self.__wrapped__,))


class composable_constructor(_CallableObjectProxy):
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

        If the other operand is a type, and is not being forced
        to be composable, this operator falls through to what
        the wrapped object and the other operand would do. For
        classes as of Python 3.10, that creates a type union.

        If the other operand is not a type, or is being forced
        to be composable, this operator creates a composed
        function which is equivalent to other(self(...)), and
        is itself composable with the | operator.
        """
        if isinstance(other, type) and not isinstance(other, composable):
            return self.__wrapped__ | other
        if not callable(other):
            return NotImplemented
        return composable(_compose(other, self))

    def __ror__(self, other):
        """Type union or function composition operator overload.

        If the other operand is a type, and is not being forced
        to be composable, this operator falls through to what
        the wrapped object and the other operand would do. For
        classes as of Python 3.10, that creates a type union.

        If the other operand is not a type, or is being forced
        to be composable, this operator creates a composed
        function which is equivalent to self(other(...)), and
        is itself composable with the | operator.
        """
        if isinstance(other, type) and not isinstance(other, composable):
            return other | self.__wrapped__
        if not callable(other):
            return NotImplemented
        return composable(_compose(self, other))

    __repr__ = composable.__repr__
    __reduce_ex__ = composable.__reduce_ex__

    def __instancecheck__(self, instance):
        """Check if instance is of the wrapped class."""
        return isinstance(instance, self.__wrapped__)

    def __subclasscheck__(self, subclass):
        """Check if subclass is of the wrapped class."""
        try:
            subclass = subclass.__wrapped__
        except AttributeError:
            pass
        return issubclass(subclass, self.__wrapped__)


class composable_instances(_CallableObjectProxy):
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

    __instancecheck__ = composable_constructor.__instancecheck__
    __subclasscheck__ = composable_constructor.__subclasscheck__
