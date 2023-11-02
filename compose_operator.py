# SPDX-License-Identifier: 0BSD
# Copyright 2022 Alexander Kozhevnikov <mentalisttraceur@gmail.com>

"""Operator overload for function composition."""

__all__ = ('composable', 'composable_constructor', 'composable_instances')
__version__ = '1.0.3'


from copy import deepcopy as _deepcopy
from inspect import unwrap as _unwrap

from compose import sacompose as _compose
from wrapt import CallableObjectProxy as _CallableObjectProxy


def _name(obj):
    return type(obj).__name__


class composable(_CallableObjectProxy):
    """Make a function composable with the | operator."""
    __slots__ = ()

    def __init__(self, function):
        """Initialize the composable function wrapper.

        Arguments:
            function: Function (or other callable) to make composable.

        Raises:
            TypeError: If the function is not callable.
        """
        if isinstance(function, composable):
            function = function.__wrapped__
        if not callable(function):
            raise TypeError(_name(self) + '() argument must be callable')
        super().__init__(function)

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

    def __get__(self, obj, objtype=None):
        """Get the wrapped function as a composable bound method."""
        wrapped = self.__wrapped__
        try:
            bind = type(wrapped).__get__
        except AttributeError:
            return self
        bound_wrapped = bind(wrapped, obj, objtype)
        if bound_wrapped is wrapped:
            return self
        return type(self)(bound_wrapped)

    def __repr__(self):
        """Represent the wrapper as an unambiguous string."""
        return f'{_name(self)}({self.__wrapped__!r})'

    def __reduce_ex__(self, protocol):
        """Reduce the wrapper for serialization."""
        return (type(self), (self.__wrapped__,))

    def __copy__(self):
        """Make a shallow copy of the wrapper."""
        return type(self)(self.__wrapped__)

    def __deepcopy__(self, memo):
        """Make a deep copy the wrapper."""
        return type(self)(_deepcopy(self.__wrapped__, memo))

    def __call__(self, /, *args, **kwargs):
        """Call the wrapped callable.

        If the return value is callable, it is made composable
        by wrapping it with the same wrapper type as this one.
        """
        result = super().__call__(*args, **kwargs)
        if callable(result):
            return type(self)(result)
        return result


def _is_forced_composable(obj):
    composable_classes = (composable, composable_constructor)
    obj = _unwrap(obj, stop=lambda obj: isinstance(obj, composable_classes))
    return isinstance(obj, composable)


class composable_constructor(_CallableObjectProxy):
    """Make a class constructor composable with the | operator."""
    __slots__ = ()

    def __init__(self, cls):
        """Initialize the composable constructor wrapper.

        Arguments:
            cls: Class whose constructor to make composable.

        Raises:
            TypeError: If cls is not a class.
        """
        if isinstance(cls, composable_constructor):
            cls = cls.__wrapped__
        if not isinstance(cls, type):
            raise TypeError(_name(self) + '() argument must be a class')
        super().__init__(cls)

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
        if isinstance(other, type) and not _is_forced_composable(other):
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
        if isinstance(other, type) and not _is_forced_composable(other):
            return other | self.__wrapped__
        if not callable(other):
            return NotImplemented
        return composable(_compose(self, other))

    __repr__ = composable.__repr__
    __reduce_ex__ = composable.__reduce_ex__
    __copy__ = composable.__copy__
    __deepcopy__ = composable.__deepcopy__

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
        """Initialize the composable instances wrapper.

        Arguments:
            cls: Class whose callable instances to make composable.

        Raises:
            TypeError: If cls is not a class.
        """
        if isinstance(cls, composable_instances):
            cls = cls.__wrapped__
        if not isinstance(cls, type):
            raise TypeError(_name(self) + '() argument must be a class')
        super().__init__(cls)

    def __call__(self, /, *args, **kwargs):
        """Construct a composable instance of the wrapped class."""
        return composable(self.__wrapped__(*args, **kwargs))

    __or__ = composable_constructor.__or__
    __ror__ = composable_constructor.__ror__

    __repr__ = composable.__repr__
    __reduce_ex__ = composable.__reduce_ex__
    __copy__ = composable.__copy__
    __deepcopy__ = composable.__deepcopy__

    __instancecheck__ = composable_constructor.__instancecheck__
    __subclasscheck__ = composable_constructor.__subclasscheck__
