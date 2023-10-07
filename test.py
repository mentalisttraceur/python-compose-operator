import typing

from compose import sacompose
from compose_operator import *


# Since the actual composition is provided by the
# `compose` package, none of these tests check if
# calling a composition does the right thing - we
# only need to check that the operator constructs
# the right composition.


# Hack the `==` of `composable` and `sacompose`
# to make the tests more clear+concise+readable:

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


# This is kinda hacky: nothing new is tested by this,
# and it creates a dependency between tests, but
# putting this definition in a test keeps any errors
# from happening until after the file is loaded by
# the test runner.
def test_composable_decorate():
    global h

    @composable
    def h(whatever):
        ...


# What do these two tests verify that wasn't already
# checked by the above? They would expose any state-
# -retaining issues, because there is one instance of
# ``composable`` (the one decorating ``h``) being used
# repeatedly. And if the prior tests pass but this fails,
# we've narrowed it down to such state-retaining issues.

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


# Same "this is kinda hacky" as `test_composable_decorate`:
def test_composable_constructor_decorate():
    global D

    @composable_constructor
    class D:
        ...


def test_composable_constructor_with_function():
    assert D | f == composable(sacompose(f, D))


def test_function_with_composable_constructor():
    assert f | D == composable(sacompose(D, f))


def test_composable_constructor_with_class():
    assert D | C == typing.Union[D, C]

def test_composable_constructor_with_itself():
    assert D | D == D


def test_composable_composable_constructor_with_class():
    assert composable(D) | C == composable(sacompose(C, composable(D)))


def test_composable_constructor_with_composable_class():
    assert D | composable(C) == composable(sacompose(composable(C), D))

def test_composable_constructor_chain():
    assert f | D | C == composable(sacompose(C, D, f))


# Same "this is kinda hacky" as `test_composable_decorate`:
def test_composable_instances_decorate():
    global F

    @composable_instances
    class F:
        def __eq__(self, other):
            return type(self) == type(other)
        def __call__(self, whatever):
            ...


def test_composable_instance_with_function():
    assert F() | f == composable(sacompose(f, F()))

def test_class_with_composable_instance():
    assert C | F() == composable(sacompose(F(), C))

def test_composable_constructor_with_composable_instances():
    assert D | F == typing.Union[D, F]

def test_composable_constructor_with_composable_instance():
    assert D | F() == composable(sacompose(F(), D))

def test_composable_constructor_with_composable_composable_instances():
    assert D | composable(F) == composable(sacompose(composable(F), D))


# Same "this is kinda hacky" as `test_composable_decorate`:
def test_composable_instances_constructor_decorate():
    global G

    @composable_constructor
    @composable_instances
    class G:
        def __eq__(self, other):
            return type(self) == type(other)
        def __call__(self, whatever):
            ...

def test_composable_instances_constructor_with_its_instance():
    assert G | G() == composable(sacompose(G(), G))

def test_composable_instances_constructor_instance_with_its_constructor():
    assert G() | G == composable(sacompose(G, G()))

def test_composable_instances_constructor_with_class():
    assert G | C == typing.Union[G, C]

def test_composable_instances_constructor_with_composable_constructor():
    assert G | D == typing.Union[G, D]

def test_composable_instances_constructor_with_composable_instances():
    assert G | F == typing.Union[G, F]

def test_composable_constructor_and_instances_with_itself():
    assert G | G == G

def test_composable_instance_constructor_with_composable_itself():
    assert G | composable(G) == composable(sacompose(composable(G), G))

def test_composable_instance_constructor_instance_with_itself():
    assert G() | G() == composable(sacompose(G(), G()))


# This is basically overkill, but order-independence matters,
# so as a compromize, shove it all in one test.
def test_composable_instances_constructor_order_independence():
    @composable_instances
    @composable_constructor
    class H:
        def __eq__(self, other):
            return type(self) == type(other)
        def __call__(self, whatever):
            ...

    assert H | H() == composable(sacompose(H(), H))
    assert H() | H == composable(sacompose(H, H()))
    assert H | C == typing.Union[H, C]
    assert H | D == typing.Union[H, D]
    assert H | F == typing.Union[H, F]
    assert H | G == typing.Union[H, G]
    assert H | H == H
    assert H | composable(H) == composable(sacompose(composable(H), H))
    assert H() | H() == composable(sacompose(H(), H()))


# Check composing ``async`` functions doesn't break making
# the compositions (the current implementation does not
# need to do anything different for ``async`` since that's
# automatically handled by ``sacompose``, but these tests
# would catch changes in `compose.sacompose` that require
# a change in this code, and changes in this code that
# don't realize they're breaking this). It's probably too
# low-value to retest literally every permutation of the
# above just with async functions swapped in, so I just
# threw some of the base cases in here:
def test_async():
    async def a(whatever):
        ...

    assert h | a == composable(sacompose(a, h))
    assert a | h == composable(sacompose(h, a))
    assert D | a == composable(sacompose(a, D))
    assert a | D == composable(sacompose(D, a))

    @composable
    async def b(whatever):
        ...

    assert a | b == composable(sacompose(b, a))
    assert b | a == composable(sacompose(a, b))
    assert C | b == composable(sacompose(b, C))
    assert b | C == composable(sacompose(C, b))

    @composable_instances
    class A:
        def __eq__(self, other):
            return type(self) == type(other)
        async def __call__(self, whatever):
            ...

    assert A() | f == composable(sacompose(f, A()))
    assert C | A() == composable(sacompose(A(), C))
    assert D | A == typing.Union[D, A]
    assert D | A() == composable(sacompose(A(), D))
    assert D | composable(A) == composable(sacompose(composable(A), D))


def test_composable_sticks_to_callable_return_values():
    def return_f():
        return f
    assert isinstance(composable(return_f)(), composable)


def test_composable_does_not_stick_to_uncallable_return_values():
    assert not isinstance(composable(f)("whatever"), composable)
