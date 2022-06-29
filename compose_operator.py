# SPDX-License-Identifier: 0BSD
# Copyright 2022 Alexander Kozhevnikov <mentalisttraceur@gmail.com>

"""TODO"""

__all__ = ('composable', 'composable_constructor', 'composable_instances')
__version__ = '0.2.0'


from compose import sacompose as _compose
from wrapt import CallableObjectProxy as _CallableObjectProxy
from wrapt import ObjectProxy as _ObjectProxy
import reprshed as _reprshed


def _name(obj):
    return type(obj).__name__


class composable(_CallableObjectProxy):
    """TODO"""
    __slots__ = ()

    def __init__(self, function):
        """TODO"""
        if isinstance(function, (composable, composable_constructor)):
            function = function.__wrapped__
        if not callable(function):
            raise TypeError(_name(self) + '() argument must be callable')
        super().__init__(function)

    def __or__(self, other):
        """TODO"""
        if not callable(other):
            return NotImplemented
        if isinstance(other, (composable, composable_constructor)):
            other = other.__wrapped__
        return type(self)(_compose(other, self.__wrapped__))

    def __ror__(self, other):
        """TODO"""
        if not callable(other):
            return NotImplemented
        if isinstance(other, (composable, composable_constructor)):
            other = other.__wrapped__
        return type(self)(_compose(self.__wrapped__, other))

    def __repr__(self):
        """TODO"""
        return _reprshed.pure(self, self.__wrapped__)

    def __reduce_ex__(self, protocol):
        """TODO"""
        return (type(self), (self.__wrapped__,))


class composable_constructor(_CallableObjectProxy):
    """TODO"""
    __slots__ = ()

    def __init__(self, cls):
        """TODO"""
        if isinstance(cls, (composable, composable_constructor)):
            cls = cls.__wrapped__
        if not isinstance(cls, type):
            raise TypeError(_name(self) + '() argument must be a class')
        super().__init__(cls)

    def __or__(self, other):
        """TODO"""
        if isinstance(other, type) and not isinstance(other, composable):
            return self.__wrapped__ | other
        return composable(self).__or__(other)

    def __ror__(self, other):
        """TODO"""
        if isinstance(other, type) and not isinstance(other, composable):
            return other | self.__wrapped__
        return composable(self).__ror__(other)

    __repr__ = composable.__repr__
    __reduce_ex__ = composable.__reduce_ex__


class composable_instances(_ObjectProxy):
    """TODO"""
    __slots__ = ()

    def __init__(self, cls):
        """TODO"""
        if not isinstance(cls, type):
            raise TypeError(_name(self) + '() argument must be a class')
        super().__init__(cls)

    def __call__(self, /, *args, **kwargs):
        """TODO"""
        return composable(self.__wrapped__(*args, **kwargs))

    __repr__ = composable.__repr__
    __reduce_ex__ = composable.__reduce_ex__
