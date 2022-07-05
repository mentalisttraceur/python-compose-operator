import typing

from compose import sacompose
from compose_operator import *


def _composable_eq(self, other):
    assert type(self) == type(other)
    assert self.__wrapped__ == other.__wrapped__
    return True
composable.__eq__ = _composable_eq


def _sacompose_eq(self, other):
    assert type(self) == type(other)
    assert self.functions == other.functions
    return True
sacompose.__eq__ = _sacompose_eq


def f(whatever):
    ...


def g(whatever):
    ...


def test_composable_left():
    assert composable(f) | g == composable(sacompose(g, composable(f)))


def test_composable_right():
    assert f | composable(g) == composable(sacompose(composable(g), f))


def h(whatever):
    ...


def test_composable_decorate():
    global h
    h = composable(h)


def test_composable_decorated_left():
    assert h | f == composable(sacompose(f, h))


def test_composable_decorated_right():
    assert f | h == composable(sacompose(h, f))


def test_composable_chain():
    assert h | g | f == composable(sacompose(f, g, h))


class C:
    ...


def test_composable_function_with_class():
    assert h | C == composable(sacompose(C, h))


def test_composable_class_with_function():
    assert composable(C) | f == composable(sacompose(f, composable(C)))


def test_composable_decorated_function_with_class():
    assert h | C == composable(sacompose(C, h))


def test_class_with_composable_class():
    assert C | composable(C) == composable(sacompose(composable(C), C))


class D:
    ...


def test_composable_constructor_decorate():
    global D
    D = composable_constructor(D)


def test_composable_constructor_decorated_class_with_function():
    assert D | f == composable(sacompose(f, D))

def test_function_with_composable_constructor_decorated_class():
    assert f | D == composable(sacompose(D, f))

def test_composable_constructor_decorated_class_with_class():
    assert D | C == typing.Union[D, C]

def test_composable_composable_constructor_decorated_class_with_class():
    assert composable(D) | C == composable(sacompose(C, composable(D)))

def test_composable_constructor_decorated_class_with_composable_class():
    assert D | composable(C) == composable(sacompose(composable(C), D))

def test_composable_constructor_chain():
    assert f | D | C == composable(sacompose(C, D, f))

def test_I_am_very_tired_TODO():
    @composable_instances
    class F:
        def __eq__(self, other):
            return type(self) == type(other)
        def __call__(self, whatever):
            ...

    assert F() | f == composable(sacompose(f, F()))
    assert C | F() == composable(sacompose(F(), C))
    assert D | F == typing.Union[D, F]
    assert D | F() == composable(sacompose(F(), D))
    assert D | composable(F) == composable(sacompose(composable(F), D))

    @composable_constructor
    @composable_instances
    class G:
        def __eq__(self, other):
            return type(self) == type(other)
        def __call__(self, whatever):
            ...

    assert G | G() == composable(sacompose(G(), G))
    assert G() | G == composable(sacompose(G, G()))
    assert G | G == G
    assert G | composable(G) == composable(sacompose(composable(G), G))
    assert G() | G() == composable(sacompose(G(), G()))

    @composable_instances
    @composable_constructor
    class H:
        def __eq__(self, other):
            return type(self) == type(other)
        def __call__(self, whatever):
            ...

    assert H | H() == composable(sacompose(H(), H))
    assert H() | H == composable(sacompose(H, H()))
    assert H | H == H
    assert H | composable(H) == composable(sacompose(composable(H), H))
    assert H() | H() == composable(sacompose(H(), H()))

    async def a(whatever):
        ...

    # Everything below needs an await, unlike any of the above:
    assert h | a == composable(sacompose(a, h))
    assert a | h == composable(sacompose(h, a))
    assert D | a == composable(sacompose(a, D))
    assert a | D == composable(sacompose(D, a))

    @composable
    async def b(whatever):
        ...

    assert f | b == composable(sacompose(b, f))
    assert b | f == composable(sacompose(f, b))
    assert C | b == composable(sacompose(b, C))
    assert b | C == composable(sacompose(C, b))
